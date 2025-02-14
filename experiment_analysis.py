import pandas as pd
import numpy as np
from scipy import stats
import hashlib
from typing import Dict, List, Union, Tuple

class ExperimentAnalysis:
    def __init__(self):
        self.alpha = 0.05  # Default significance level
    
    @staticmethod
    def apollo_bucket(experiment_name: str, individual_id: Union[str, List[str], int, float]) -> Union[int, Tuple[List[int], List]]:
        """
        Generate consistent bucket numbers (0-99) for experimental units.
        
        Args:
            experiment_name (str): Name of the experiment for consistent bucketing
            individual_id (str/list/int/float): Individual identifier(s) to be bucketed
        
        Returns:
            Union[int, Tuple[List[int], List]]: Bucket number(s) for the individual(s)
        """
        def _single_apollo_bucket(exp_name: str, ind_id: Union[str, int, float]) -> int:
            sha1 = hashlib.sha1()
            if isinstance(ind_id, (float, int)):
                ind_id = '{:.0f}'.format(ind_id)
            else:
                ind_id = str(ind_id)
            raw_key = ind_id + exp_name + 'exp_bucket'
            sha1.update(bytes(raw_key, encoding='UTF-8'))
            sha1_int = int.from_bytes(sha1.digest()[-4:], byteorder='big')
            return sha1_int % 100

        if isinstance(individual_id, list):
            return [_single_apollo_bucket(experiment_name, x) for x in individual_id], individual_id
        return _single_apollo_bucket(experiment_name, individual_id)

    @staticmethod
    def assign_groups(bucket_number: int, group_proportions: Dict[str, Union[str, float, int]]) -> str:
        """
        Assign groups based on bucket number and group proportions.
        
        Args:
            bucket_number (int): Bucket number (0-99)
            group_proportions (dict): Dictionary of group names and their proportions
        
        Returns:
            str: Assigned group name
        """
        def extract_percentage(input_value: Union[str, float, int]) -> int:
            if isinstance(input_value, str):
                if input_value.endswith('%'):
                    return int(input_value[:-1])
                try:
                    float_value = float(input_value)
                    return int(float_value * 100) if 0 <= float_value <= 1 else int(float_value)
                except ValueError:
                    raise ValueError(f"Invalid input string: {input_value}")
            elif isinstance(input_value, (float, int)):
                return int(input_value * 100) if 0 <= input_value <= 1 else int(input_value)
            raise ValueError("Input must be a string, integer, or float.")

        total_percentage = sum(extract_percentage(val) for val in group_proportions.values())
        if total_percentage != 100:
            raise ValueError("The sum of all proportions must equal 100")

        start_bucket = 0
        for group, prop in group_proportions.items():
            prop = extract_percentage(prop)
            if start_bucket <= bucket_number < start_bucket + prop:
                return group
            start_bucket += prop
        return list(group_proportions.keys())[-1]  # Return last group if no match found

    def _get_confidence_interval(self, point_estimate: float, std_error: float, 
                               is_two_sided: bool = True, alternative: str = 'two-sided') -> List[float]:
        """Calculate confidence interval based on test type."""
        if is_two_sided:
            z_value = stats.norm.ppf(1 - self.alpha/2)
            margin = z_value * std_error
            return [
                round(point_estimate - margin, 6),
                round(point_estimate + margin, 6)
            ]
        else:
            z_value = stats.norm.ppf(1 - self.alpha)
            if alternative == 'less':
                return [float('-inf'), round(point_estimate + z_value * std_error, 6)]
            else:  # alternative == 'greater'
                return [round(point_estimate - z_value * std_error, 6), float('inf')]

    def test_mean(self, data: pd.DataFrame, groupname: str, treated_label: str, 
                  control_label: str, test_metric: str, is_two_sided: bool = True, 
                  alternative: str = 'two-sided') -> List:
        """Conduct t-test for mean metrics."""
        treated = data[data[groupname] == treated_label][test_metric]
        control = data[data[groupname] == control_label][test_metric]
        
        treated_mean = treated.mean()
        control_mean = control.mean()
        
        mae = treated_mean - control_mean
        mape = treated_mean / control_mean - 1
        
        t_stats, pval = stats.ttest_ind(treated, control, equal_var=False)
        
        std_error = np.sqrt(
            np.var(treated, ddof=1) / len(treated) +
            np.var(control, ddof=1) / len(control)
        )
        
        ci = self._get_confidence_interval(mae, std_error, is_two_sided, alternative)
        
        p_value = pval if is_two_sided else (
            pval / 2 if (t_stats < 0 and alternative == 'less') or 
            (t_stats > 0 and alternative == 'greater') else 1 - pval / 2
        )
        
        sig = "显著" if p_value < self.alpha else "不显著"
        
        return [treated_mean, control_mean, mae, mape, t_stats, p_value, ci, sig]

    def _get_ratio_variance(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate variance for ratio metrics."""
        x_var = np.var(x, ddof=1)/len(x)
        y_var = np.var(y, ddof=1)/len(y)
        x_mean, y_mean = np.mean(x), np.mean(y)
        cov = np.cov(x, y)[0,1]/len(x)
        
        return (1/pow(y_mean,2)*x_var + 
                pow(x_mean,2)/pow(y_mean,4)*y_var - 
                2*x_mean/pow(y_mean,3)*cov)

    def test_ratio(self, data: pd.DataFrame, groupname: str, treated_label: str,
                   control_label: str, x_var: str, y_var: str, is_two_sided: bool = True,
                   alternative: str = 'two-sided') -> List:
        """Conduct statistical test for ratio metrics."""
        treated_data = data[data[groupname] == treated_label]
        control_data = data[data[groupname] == control_label]
        
        x_treated, y_treated = treated_data[x_var], treated_data[y_var]
        x_control, y_control = control_data[x_var], control_data[y_var]
        
        treated_ratio = np.sum(x_treated) / np.sum(y_treated)
        control_ratio = np.sum(x_control) / np.sum(y_control)
        
        diff = treated_ratio - control_ratio
        relative_diff = diff / control_ratio
        
        std_error = np.sqrt(
            self._get_ratio_variance(x_treated, y_treated) +
            self._get_ratio_variance(x_control, y_control)
        )
        
        t_stat = diff / std_error
        ci = self._get_confidence_interval(diff, std_error, is_two_sided, alternative)
        
        if is_two_sided:
            p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        else:
            p_value = (stats.norm.cdf(t_stat) if alternative == 'less' 
                      else 1 - stats.norm.cdf(t_stat))
        
        sig = "显著" if p_value < self.alpha else "不显著"
        
        return [treated_ratio, control_ratio, diff, relative_diff, t_stat, p_value, ci, sig]

    def test_proportion(self, data: pd.DataFrame, groupname: str, treated_label: str,
                       control_label: str, metric: str, is_two_sided: bool = True,
                       alternative: str = 'two-sided') -> List:
        """Conduct binomial test for proportion metrics."""
        treated = data[data[groupname] == treated_label][metric]
        control = data[data[groupname] == control_label][metric]
        
        treated_rate = treated.mean()
        control_rate = control.mean()
        
        diff = treated_rate - control_rate
        relative_diff = diff / control_rate
        
        std_error = np.sqrt(
            treated_rate*(1-treated_rate)/len(treated) +
            control_rate*(1-control_rate)/len(control)
        )
        
        t_stat = diff / std_error
        ci = self._get_confidence_interval(diff, std_error, is_two_sided, alternative)
        
        if is_two_sided:
            p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        else:
            p_value = (stats.norm.cdf(t_stat) if alternative == 'less'
                      else 1 - stats.norm.cdf(t_stat))
        
        sig = "显著" if p_value < self.alpha else "不显著"
        
        return [treated_rate, control_rate, diff, relative_diff, t_stat, p_value, ci, sig]

    def run_statistical_tests(self, data: pd.DataFrame, metrics: List[str], 
                            metric_types: List[str], groupname: str,
                            treated_labels: Union[str, List[str]], control_label: str,
                            is_two_sided: bool = True,
                            alternative: str = 'two-sided') -> pd.DataFrame:
        """
        Run statistical tests for multiple metrics and multiple treatment groups.
        
        Args:
            data (pd.DataFrame): Input dataset
            metrics (List[str]): List of metrics to test
            metric_types (List[str]): List of metric types ('mean', 'ratio', or 'proportion')
            groupname (str): Column name containing group labels
            treated_labels (str or List[str]): Label(s) for treatment group(s)
            control_label (str): Label for control group
            is_two_sided (bool): Whether to perform two-sided test
            alternative (str): 'two-sided', 'less', or 'greater'
        
        Returns:
            pd.DataFrame: Statistical test results
        """
        # Convert single treatment label to list for consistent processing
        if isinstance(treated_labels, str):
            treated_labels = [treated_labels]
        
        results = []
        for treated_label in treated_labels:
            for metric, metric_type in zip(metrics, metric_types):
                if metric_type == 'mean':
                    result = self.test_mean(data, groupname, treated_label, control_label,
                                          metric, is_two_sided, alternative)
                elif metric_type == 'ratio':
                    x_var, y_var = metric.split('/')
                    result = self.test_ratio(data, groupname, treated_label, control_label,
                                           x_var, y_var, is_two_sided, alternative)
                elif metric_type == 'proportion':
                    result = self.test_proportion(data, groupname, treated_label, control_label,
                                               metric, is_two_sided, alternative)
                else:
                    raise ValueError(f"Unsupported metric type: {metric_type}")
                
                results.append([treated_label, metric] + result)
        
        results_df = pd.DataFrame(
            results,
            columns=['Treatment_Group', 'Metric', 'Treatment_Value', 'Control_Value',
                    'Absolute_Diff', 'Relative_Diff', 'T_Statistic', 'P_Value',
                    'Confidence_Interval', 'Significance']
        )
        
        # Round all numeric columns to 6 decimal places
        numeric_columns = ['Treatment_Value', 'Control_Value', 'Absolute_Diff', 
                         'Relative_Diff', 'T_Statistic', 'P_Value']
        for col in numeric_columns:
            results_df[col] = results_df[col].apply(lambda x: round(x, 6) if isinstance(x, (int, float)) else x)
        
        # Round values in Confidence_Interval
        results_df['Confidence_Interval'] = results_df['Confidence_Interval'].apply(
            lambda x: [round(x[0], 6), round(x[1], 6)] if isinstance(x[0], (int, float)) else x
        )
        
        return results_df