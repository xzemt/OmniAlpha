# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union

# 尝试导入 Qlib 的 XGBoost 模型
# 这是一个基于 Qlib 框架的封装，通常需要 Qlib 的数据环境支持
try:
    from qlib.contrib.model.xgboost import XGBModel
    from qlib.data.dataset import DatasetH, TSDatasetH
    from qlib.data.dataset.handler import DataHandlerLP
    HAS_QLIB = True
except ImportError:
    HAS_QLIB = False
    print("Warning: qlib not found or not installed correctly. Using fallback mode.")
    # 定义个空类防止报错
    class XGBModel:
        def __init__(self, **kwargs): pass
        def fit(self, dataset, **kwargs): pass
        def predict(self, dataset, **kwargs): return np.array([])


class QlibXGBoostAlphaModel:
    """
    封装 Qlib 中的 XGBoost 模型，用于 Alpha 因子的自动选择与组合。
    
    主要功能：
    1. 接收因子数据进行训练
    2. 利用 XGBoost 的特征重要性进行 Alpha 筛选
    3. 输出预测得分用于选股
    """

    def __init__(self, model_params: Optional[Dict] = None):
        """
        初始化模型
        :param model_params: XGBoost 模型参数字典
        """
        self.default_params = {
            'estimator': 'xgboost',
            'n_estimators': 600,
            'max_depth': 6,
            'min_child_weight': 1,
            'eta': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'objective': 'reg:squarederror',
            'nthread': 4,
            'tree_method': 'hist',
            'eval_metric': 'rmse',
            'missing': np.nan 
        }
        
        if model_params:
            self.default_params.update(model_params)
            
        # Qlib 的 XGBModel 接受参数作为 kwargs
        if HAS_QLIB:
            self.model = XGBModel(**self.default_params)
        else:
            self.model = None

    def fit(self, dataset):
        """
        训练模型
        :param dataset: Qlib 的 Dataset 对象 (如 TSDatasetH)
        """
        if not HAS_QLIB:
            raise ImportError("Qlib is not installed.")
        
        self.model.fit(dataset)

    def predict(self, dataset) -> pd.Series:
        """
        预测
        :param dataset: Qlib 的 Dataset 对象
        :return: 预测分数 Series
        """
        if not HAS_QLIB:
            raise ImportError("Qlib is not installed.")
            
        return self.model.predict(dataset)

    def get_feature_importances(self) -> Dict[str, float]:
        """
        获取特征重要性 (Alpha 因子权重)
        :return: 因子名称 -> 重要性分数 的字典
        """
        if not HAS_QLIB or self.model is None:
            return {}
            
        # Qlib 的 XGBModel 将底层 booster 对象存储在 self.model.model 中 (如果 fit 过)
        # 或者直接是 self.model (取决于具体版本实现，通常 Qlib 只是 wrapper)
        # 查看 Qlib 源码，XGBModel.fit 之后 self.model 是 xgb.Dataset / Booster
        # 准确来说，XGBModel 类有一个属性 `model` 保存了训练好的 booster
        
        try:
            booster = self.model.model
            # 获取重要性，使用 'gain' (收益) 作为衡量标准
            scores = booster.get_score(importance_type='gain')
            return scores
        except Exception as e:
            print(f"Error getting feature importances: {e}")
            return {}

    def select_top_alphas(self, top_k: int = 10) -> List[str]:
        """
        根据训练结果自动选择最重要的 Top K Alpha 因子
        :param top_k: 选择数量
        :return: 因子名称列表
        """
        importances = self.get_feature_importances()
        if not importances:
            return []
            
        # 排序
        sorted_alphas = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_alphas[:top_k]]

class DataFrameToQlibAdapter:
    """
    (可选) 简易适配器，帮助将 pandas DataFrame 转换为 Qlib 模型可能接受的格式。
    注意：Qlib 标准流程依赖 DataHandler 和 binary 数据，这里主要用于演示或非标准数据流。
    """
    # 这是一个占位符，因为正确构建 Qlib Dataset 需要较多上下文
    pass
