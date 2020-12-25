from sklearn.feature_selection import (
    chi2,
    f_classif,
    f_regression,
    mutual_info_classif,
    mutual_info_regression,
    SelectKBest,
    SelectPercentile,
)


class UnivariateFeatureSelection:
    """Univariate feature selection

    n_features -> can be int or float, how many features to choose
    is_classification -> is this a classification or regression
    scoring -> what scoring method should we use

    This function is adapted from Abhishek Thakur
  """

    def __init__(self, n_features: int, is_classification: bool, scoring: str):
        valid_scoring = (
            {
                "f_classif": f_classif,
                "chi2": chi2,
                "mutual_info_classif": mutual_info_classif,
            }
            if is_classification
            else {
                "f_regression": f_regression,
                "mutual_info_regression": mutual_info_regression,
            }
        )
        if scoring not in valid_scoring:
            raise ValueError("Invalid scoring function")

        if isinstance(n_features, int):
            self.selection = SelectKBest(valid_scoring[scoring], k=n_features)
        elif isinstance(n_features, float):
            self.selection = SelectPercentile(
                valid_scoring[scoring], percentile=int(n_features * 100)
            )
        else:
            raise ValueError("n_features must be a float or an int")

    def fit(self, X, y):
        return self.selection.fit(X, y)

    def transform(self, X, y):
        return self.selection.transform(X, y)

    def fit_transform(self, X, y):
        return self.selection.fit_transform(X, y)

