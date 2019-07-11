import pandas as pd
from DecisionTreeModel.visualization import *
import math

def getWaterMelonData(version_no=2):
    '''
    获取西瓜数据集,
    :param version_no: 数据集版本号
    :return: 数据集，特征名称，标签名称
    '''

    if version_no == 2:
        dataset = pd.read_csv(
            './data/WaterMelonDataset2.csv',
            index_col='编号'
        )
        feature_names = [
            '色泽', '根蒂', '敲声',
            '纹理', '脐部', '触感'
        ]

    elif version_no == 3:
        dataset = pd.read_csv(
            './data/WaterMelonDataset3.csv',
            index_col='编号'
        )
        feature_names = [
            '色泽', '根蒂', '敲声', '纹理',
            '脐部', '触感',
            # '密度', '含糖率'
        ]

    label_names = '好瓜'

    features_info = {
        '色泽': 'dispersed',
        '根蒂': 'dispersed',
        '敲声': 'dispersed',
        '纹理': 'dispersed',
        '脐部': 'dispersed',
        '触感': 'dispersed',
        '密度': 'series',
        '含糖率': 'series',
    }

    return dataset, feature_names, label_names, features_info

def getTrainTestData(dataset):
    '''
    获取训练集与测试集，按照西瓜书的划分
    :param dataset:
    :return:
    '''
    # 训练集的索引值
    train_data_index = [1, 2, 3, 6, 7, 10, 14, 15, 16, 17]
    # 测试集的索引值
    test_data_index = [4, 5, 8, 9, 11, 12, 13]
    train_data = dataset.loc[train_data_index]
    test_data = dataset.loc[test_data_index]
    return train_data, test_data

class DecisionTree(object):
    def __init__(self, dataset, feature_names, label_name):
        '''
        初始化决策树
        :param dataset: 待处理的数据集
        :param features_name: 特征名称
        :param label_names: 标签名称
        '''
        self.feature_names = feature_names
        self.label_name = label_name
        # 计算特征与标签的所有特征值
        self.unique_value = {}
        self.getUniqueValue(dataset)

    def getUniqueValue(self, dataset):
        '''
        计算原始数据集中所有特征值
        :return:
        '''
        for feaure_name in self.feature_names:
            self.unique_value[feaure_name] = list(dataset[feaure_name].unique())

    def classifyMethod(self, dataset, feature_names, method):
        '''
        划分特征值的标准，默认选择为信息增益划分
        :param method: 划分特征值的标准
        :return:
        '''
        classify_feature = {}
        # 如果是信息增益方式的话，选择信息增益最大的特征
        if method == 'gain':
            columns = ['gain']
            for feature_name in feature_names:
                classify_feature[feature_name] = calculateGain(
                    dataset, feature_name, self.label_name
                )
            classify_feature = pd.DataFrame(classify_feature, index=columns).T
            # print(classify_feature)
            # 返回最大值的索引（特征名称）
            return classify_feature.idxmax().values[0]

        # 先选出信息增益高于平均水平的属性，再从中选择增益率最高的特征
        elif method == 'gain_ratio':
            columns = ['gain_ratio', 'IV', 'gain']
            for feature_name in feature_names:
                classify_feature[feature_name] = calculateGainRatio(
                    dataset, feature_name, self.label_name
                )
            classify_feature = pd.DataFrame(classify_feature, index=columns).T
            # 选出信息增益高于平均水平的属性
            high_gain_dataset = classify_feature[classify_feature['gain'] > classify_feature['gain'].mean()]
            # 从中选择增益率最高的特征
            return high_gain_dataset[['gain_ratio']].idxmax().values[0]

        # 选出基尼指数最小的属性
        elif method == 'gini':
            columns = ['gini']
            for feature_name in feature_names:
                classify_feature[feature_name] = calculateGiniIndex(
                    dataset, feature_name, self.label_name
                )
            classify_feature = pd.DataFrame(classify_feature, index=columns).T
            # print(classify_feature)
            return classify_feature[['gini']].idxmin().values[0]

    def getMaxNumLabel(self, dataset, label_values):
        '''
        选出dataset中类别数量最多的标签名称
        :param dataset: 当前数据集
        :param label_values: 当前数据集中所包含的类
        :return:
        '''
        max_label = None
        max_count = 0
        for label_value in label_values:
            label_num = dataset[dataset[self.label_name] == label_value].shape[0]
            if label_num > max_count:
                max_label = label_value
                max_count = label_num
        return max_label

    def predict(self, data, node):
        '''
        对数据进行预测
        :param test_data: 待预测的数据
        :param node: 决策树，若非字典形式，则说明node是分类标签
        :return: 预测结果
        '''
        # 按照测数据集遍历决策树，如果当前节点是字典，则说明未到叶子节点
        while type(node).__name__ == 'dict':
            # 从决策树中取出特征
            feature = list(node.keys())[0]
            # 如果测试数据中有该特征
            if feature in data:
                # 先从测试数据中取出对应的特征值，再在决策树中找相应的子树
                node = node[feature][data[feature]]
            else:
                print('数据缺失')
        return node

    def accurate(self, dataset, tree_root):
        '''
        判断测试数据集的正确率
        :param test_dataset: 待预测的测试数据集
        :param tree_root: 决策树的根节点
        :return: 正确率，与正确的个数
        '''
        data_index = dataset.index.tolist()
        right_count = 0
        # 遍历每一行测试数据
        for i_index in data_index:
            df = dataset.loc[i_index]
            # 将dataframe格式的数据转成字典形式
            data = df.to_dict()
            result = self.predict(data, tree_root)
            if result == data[self.label_name]:
                right_count += 1
        return right_count / len(data_index), right_count

################################创建决策树############################################

    # def createDecisionTree(self, dataset, feature_names, method='gain'):
    #     '''
    #     构造决策树
    #     :param dataset: 构造树需要用到的数据集
    #     :param features_name: 构造树需要用到的特征名称
    #     :param method: 判定最优特征的方法
    #     :return: 当前生成的子树节点
    #     '''
    #     # 选出当前数据集中所有类的取值
    #     label_values = list(dataset[self.label_name].unique())
    #     # 选出当前数据集中最多的类
    #     max_label = self.getMaxNumLabel(dataset, label_values)
    #
    #     # 如果数据集中的类标签只有一种，则返回该标签
    #     if len(label_values) == 1:
    #         # return {self.label_name: {max_label}}
    #         return max_label
    #     # 如果待分类的特征为空 或者 检查数据集中的特征种类是否为1（数据集中所有特征都相同）
    #     elif len(feature_names) == 0 or dataset.drop_duplicates(subset=feature_names, keep=False).empty:
    #         # 选取当前数据集中最多的标签作为该类标签
    #         # return {self.label_name: {max_label}}
    #         return max_label
    #
    #     # 选出最佳的分类特征
    #     classify_feature = self.classifyMethod(dataset, feature_names, method=method)
    #     # 初始化节点
    #     DTree = {classify_feature: {}}
    #
    #     # feature_values = list(dataset[classify_feature].unique())
    #     feature_values = self.unique_value[classify_feature]
    #     # 对数据集进行分类
    #     for feature_value in feature_values:
    #         sub_dataset = dataset[dataset[classify_feature] == feature_value]
    #         # print('划分节点:', classify_feature)
    #         # print('划分特征:', feature_value)
    #         # print('子数据集')
    #         # print(sub_dataset)
    #         # print('=========================')
    #         # 如果数据集为空
    #         if sub_dataset.shape[0] == 0:
    #             # DTree[classify_feature][feature_value] = {self.label_name: {max_label}}
    #             DTree[classify_feature][feature_value] = max_label
    #         else:
    #             # 将特征复制一份，传递给子数据集
    #             sub_feature_names = feature_names.copy()
    #             sub_feature_names.remove(classify_feature)
    #
    #             DTree[classify_feature][feature_value] = self.createDecisionTree(
    #                 sub_dataset, sub_feature_names, method=method
    #             )
    #     return DTree


################################创建枝决策树######################################
    def isPrune(
            self, max_label, feature_values,
            classify_feature, label_values,
            train_dataset, test_dataset
    ):
        '''
        判断子树特征是否要剪枝
        :param max_label: 当前数据集中数量最多的标签，模拟剪枝后，该节点赋予的标签
        :param feature_values: 当前数据集中的特征值种类
        :param classify_feature: 最佳特征，也是是否剪枝的对象
        :param label_values: 数据标签取值的种类
        :param train_dataset: 当前的训练数据子集
        :param test_dataset:  测试数据集
        :return: 是否剪枝的标志
        '''
        # 不对特征划分时测试集的正确率与正确的数目
        prune_acc, prune_right_count = self.accurate(
            test_dataset,
            max_label
        )
        # print('剪枝后的正确率：', prune_right_count)

        # 针对划分节点生成决策树
        unprune_tree = {classify_feature: {}}

        for feature_value in feature_values:
            sub_dataset = train_dataset[train_dataset[classify_feature] == feature_value]
            # 选出当前子数据集中最多的类
            sub_max_label = self.getMaxNumLabel(sub_dataset, label_values)
            unprune_tree[classify_feature][feature_value] = sub_max_label
        # print("生成的子树")
        # createPlot(unprune_tree)

        # 不对特征划分时测试集的正确率与正确的数目
        unprune_acc, unprune_right_count = self.accurate(
            test_dataset,
            unprune_tree
        )
        # print('未剪枝的正确率：', unprune_right_count)

        if prune_acc >= unprune_acc:
            return True
        else:
            return False

    def createDecisionTree(
            self, train_dataset, test_dataset,
            feature_names, method='gain', prune=None
    ):
        '''
        :param train_dataset: 构造树需要用到的训练数据集
        :param test_dataset: 构造树需要用到的测试数据集
        :param feature_names: 构造树需要用到的特征名称
        :param method: 判定最优特征的方法
        :param prune: 决策树是否需要进行剪枝操作<PrePrune，PostPrune>
        :return: 当前生成的子树节点
        '''
        # print("当前训练的数据")
        # print(train_dataset)
        # 选出当前数据集中所有类的取值
        label_values = list(train_dataset[self.label_name].unique())

        # 选出当前数据集中最多的类
        max_label = self.getMaxNumLabel(train_dataset, label_values)

        # 如果当前数据集中只包含一种类
        if len(label_values) == 1:
            return max_label
        # 如果待分类的特征为空 或者 检查数据集中的特征种类是否为1（数据集中所有特征都相同）
        elif len(feature_names) == 0 or train_dataset.drop_duplicates(subset=feature_names, keep=False).empty:
            # 选取当前数据集中最多的标签作为该类标签
            return max_label
        else:
            # 选出最佳的分类特征
            classify_feature = self.classifyMethod(train_dataset, feature_names, method=method)
            feature_values = self.unique_value[classify_feature]

            # 是否开启剪枝？
            # 如果是PrePrune，则代表预剪枝
            if prune == 'PrePrune':
                print('是否剪枝？', classify_feature)
                if self.isPrune(
                        max_label, feature_values, classify_feature,
                        label_values, train_dataset, test_dataset
                ):
                    print('剪枝')
                    return max_label
                else:
                    print('保留')

            # 初始化节点
            DTree = {classify_feature: {}}
            # 对数据集进行分类
            for feature_value in feature_values:
                sub_dataset = train_dataset[train_dataset[classify_feature] == feature_value]
                # 如果数据集为空
                if sub_dataset.shape[0] == 0:
                    DTree[classify_feature][feature_value] = max_label
                else:
                    # 将特征复制一份，传递给子数据集
                    sub_feature_names = feature_names.copy()
                    sub_feature_names.remove(classify_feature)
                    print(classify_feature, ':', feature_value)
                    DTree[classify_feature][feature_value] = self.createDecisionTree(
                        sub_dataset, test_dataset,
                        sub_feature_names, method=method, prune=prune
                    )
            return DTree


def calculateEnt(dataset, label_name):
    '''
    计算dataset的信息熵: Ent(D)=-\sum_{k=1}^{|Y|} \frac{1}{|y|}log_2\frac{1}{|y|}=log_2|y|
    :param dataset:特征数据信息
    :param label_name: 标签名称
    :return:信息熵
    '''
    # 列举出类标签所有可能的取值
    label_values = list(dataset[label_name].unique())
    Ent = 0
    for label_value in label_values:
        tmp_data = dataset[dataset[label_name] == label_value]
        # 计算某一类的概率
        prob = tmp_data.shape[0] / dataset.shape[0]
        Ent += prob * math.log2(prob)
    return -Ent

def calculateGain(dataset, feature_name, label_name):
    '''
    计算dataset中特征为feature_name的信息增益
    :param dataset:数据信息
    :param label: 标签数据
    :return:信息增益，以及对应的条件熵
    '''
    # 计算类标签的信息熵
    Ent = calculateEnt(dataset, label_name)
    # 计算特征为feature_name的条件信息熵
    feature_values = list(dataset[feature_name].unique())
    condition_Ent = 0
    for feature_value in feature_values:
        # 选出特征feature_name中特征值为feature_value的数据
        sub_data = dataset[dataset[feature_name] == feature_value]
        # 计算概率
        prob = sub_data.shape[0] / dataset.shape[0]
        condition_Ent += prob * calculateEnt(sub_data, label_name)
    return Ent - condition_Ent

def calculateGainRatio(dataset, feature_name, label_name):
    '''
    计算dataset中特征为feature_name的信息增益
    :param dataset:数据信息
    :param feature_values:数据信息
    :param label_name: 标签数据
    :return:信息增益
    '''
    # 计算信息增益
    Gain = calculateGain(dataset, feature_name, label_name)
    # 计算特征为feature_name的IV值
    feature_values = list(dataset[feature_name].unique())
    IV = 0
    for feature_value in feature_values:
        # 选出特征feature_name中特征值为feature_value的数据
        sub_data = dataset[dataset[feature_name] == feature_value]
        # 计算概率
        prob = sub_data.shape[0] / dataset.shape[0]
        IV += prob * math.log2(prob)

    return -Gain/IV, -IV, Gain

def calculateGini(dataset, label_name):
    '''
    计算dataset中特征为feature_name的基尼系数
    :param dataset:数据信息
    :param label_name: 标签数据
    :return:基尼系数
    '''
    label_values = list(dataset[label_name].unique())
    condition_prob = 0
    for label_value in label_values:
        # 选出特征feature_name中特征值为feature_value的数据
        sub_data = dataset[dataset[label_name] == label_value]
        # 计算概率
        condition_prob += (sub_data.shape[0] / dataset.shape[0])**2
    return 1 - condition_prob

def calculateGiniIndex(dataset, feature_name, label_name):
    '''
    计算dataset中特征为feature_name的基尼系数
    :param dataset:数据信息
    :param feature_values:数据信息
    :param label_name: 标签数据
    :return:基尼系数
    '''
    feature_values = list(dataset[feature_name].unique())
    Gini_index = 0
    for feature_value in feature_values:
        # 选出特征feature_name中特征值为feature_value的数据
        sub_data = dataset[dataset[feature_name] == feature_value]
        Gini = calculateGini(sub_data, label_name)
        # 计算概率
        Gini_index += (sub_data.shape[0] / dataset.shape[0]) * Gini
    return Gini_index

if __name__ == '__main__':
    # # 构建基础决策树
    # dataset, feature_names, label_names, features_info = getWaterMelonData(2)
    # DTObject = DecisionTree(dataset, feature_names, label_names)
    # # DTObject.classifyMethod(dataset, feature_names, 'gain')
    # DTObject.root = DTObject.createDecisionTree(dataset, None, feature_names, 'gain')
    # print(DTObject.root)
    # createPlot(DTObject.root)

    # 构建剪枝决策树
    dataset1, feature_names1, label_names1, features_info = getWaterMelonData(3)
    train_dataset, test_dataset = getTrainTestData(dataset1)
    DTObject = DecisionTree(train_dataset, feature_names1, label_names1)
    DTObject.root = DTObject.createDecisionTree(
        train_dataset, test_dataset,
        feature_names1, method='gain', prune=None
    )
    # DTObject.predict(test_dataset, DTObject.root)
    # print(DTObject.root)
    createPlot(DTObject.root)
