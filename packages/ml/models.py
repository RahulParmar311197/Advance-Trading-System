from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal
from math import sqrt
from typing import Sequence

from packages.ml.datasets import FeatureDataset
from packages.regime.detector import Regime


@dataclass(frozen=True, slots=True)
class NearestCentroidClassifier:
    """Dependency-free deterministic multiclass nearest-centroid baseline."""

    labels: tuple[Regime, ...] = ()
    centroids: tuple[tuple[Decimal, ...], ...] = ()

    @classmethod
    def fit(cls, dataset: FeatureDataset) -> "NearestCentroidClassifier":
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        centroids: list[tuple[Decimal, ...]] = []
        for label in labels:
            rows = [row for row, current in zip(dataset.features, dataset.labels) if current == label]
            centroid = tuple(
                sum((row[index] for row in rows), Decimal("0")) / Decimal(len(rows))
                for index in range(len(rows[0]))
            )
            centroids.append(centroid)
        return cls(labels=labels, centroids=tuple(centroids))

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.centroids:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        if len(vector) != len(self.centroids[0]):
            raise ValueError("feature width does not match fitted classifier")
        distances = tuple(
            sum(((value - center) ** 2 for value, center in zip(vector, centroid)), Decimal("0"))
            for centroid in self.centroids
        )
        return self.labels[distances.index(min(distances))]

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


@dataclass(frozen=True, slots=True)
class LogisticRegressionClassifier:
    """Dependency-free deterministic one-vs-rest logistic-regression baseline."""

    labels: tuple[Regime, ...] = ()
    weights: tuple[tuple[Decimal, ...], ...] = ()
    biases: tuple[Decimal, ...] = ()
    learning_rate: Decimal = Decimal("0.1")
    epochs: int = 500
    l2: Decimal = Decimal("0")

    @classmethod
    def fit(
        cls,
        dataset: FeatureDataset,
        learning_rate: Decimal = Decimal("0.1"),
        epochs: int = 500,
        l2: Decimal = Decimal("0"),
    ) -> "LogisticRegressionClassifier":
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if epochs <= 0:
            raise ValueError("epochs must be positive")
        if l2 < 0:
            raise ValueError("l2 must be non-negative")
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        rows = dataset.features
        width = len(rows[0])
        trained_weights: list[tuple[Decimal, ...]] = []
        trained_biases: list[Decimal] = []
        n = Decimal(len(rows))
        for label in labels:
            weights = [Decimal("0") for _ in range(width)]
            bias = Decimal("0")
            for _ in range(epochs):
                gradients = [Decimal("0") for _ in range(width)]
                bias_gradient = Decimal("0")
                for row, current in zip(rows, dataset.labels):
                    target = Decimal("1") if current == label else Decimal("0")
                    probability = _sigmoid(_dot(row, weights) + bias)
                    error = probability - target
                    bias_gradient += error
                    for index, value in enumerate(row):
                        gradients[index] += error * value
                for index in range(width):
                    gradients[index] = gradients[index] / n + l2 * weights[index]
                    weights[index] -= learning_rate * gradients[index]
                bias -= learning_rate * bias_gradient / n
            trained_weights.append(tuple(weights))
            trained_biases.append(bias)
        return cls(
            labels=labels,
            weights=tuple(trained_weights),
            biases=tuple(trained_biases),
            learning_rate=learning_rate,
            epochs=epochs,
            l2=l2,
        )

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.weights:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        if len(vector) != len(self.weights[0]):
            raise ValueError("feature width does not match fitted classifier")
        scores = tuple(_dot(vector, weight) + bias for weight, bias in zip(self.weights, self.biases))
        return self.labels[scores.index(max(scores))]

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


@dataclass(frozen=True, slots=True)
class _TreeNode:
    label: Regime | None = None
    feature_index: int | None = None
    threshold: Decimal | None = None
    left: "_TreeNode | None" = None
    right: "_TreeNode | None" = None


@dataclass(frozen=True, slots=True)
class RandomForestClassifier:
    """Dependency-free deterministic random-forest classification baseline.

    Each tree uses bootstrap sampling and a deterministic random subset of
    features at each split. The random seed is part of the fitted model so the
    forest can be reproduced exactly from the same dataset and configuration.
    """

    labels: tuple[Regime, ...] = ()
    trees: tuple[_TreeNode, ...] = ()
    seed: int = 0
    n_trees: int = 25
    max_depth: int = 4
    min_samples_split: int = 2
    max_features: int | None = None

    @classmethod
    def fit(
        cls,
        dataset: FeatureDataset,
        n_trees: int = 25,
        max_depth: int = 4,
        min_samples_split: int = 2,
        max_features: int | None = None,
        seed: int = 0,
    ) -> "RandomForestClassifier":
        labels = tuple(sorted(set(dataset.labels)))
        if len(labels) < 2:
            raise ValueError("at least two distinct labels are required")
        if n_trees <= 0:
            raise ValueError("n_trees must be positive")
        if max_depth <= 0:
            raise ValueError("max_depth must be positive")
        if min_samples_split < 2:
            raise ValueError("min_samples_split must be at least two")
        width = len(dataset.features[0])
        if max_features is not None and not 1 <= max_features <= width:
            raise ValueError("max_features must be between one and feature width")
        rng = random.Random(seed)
        trees = []
        rows = dataset.features
        labels_for_rows = dataset.labels
        for _ in range(n_trees):
            sample_indices = [rng.randrange(len(rows)) for _ in rows]
            trees.append(
                _fit_tree(
                    rows,
                    labels_for_rows,
                    sample_indices,
                    depth=0,
                    max_depth=max_depth,
                    min_samples_split=min_samples_split,
                    max_features=max_features,
                    rng=rng,
                )
            )
        return cls(
            labels=labels,
            trees=tuple(trees),
            seed=seed,
            n_trees=n_trees,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            max_features=max_features,
        )

    def predict(self, features: Sequence[Decimal]) -> Regime:
        if not self.trees:
            raise ValueError("classifier is not fitted")
        vector = tuple(features)
        width = _tree_width(self.trees[0])
        if len(vector) != width:
            raise ValueError("feature width does not match fitted classifier")
        votes = tuple(_predict_tree(tree, vector) for tree in self.trees)
        return min(self.labels, key=lambda label: (-votes.count(label), self.labels.index(label)))

    def predict_many(self, features: Sequence[Sequence[Decimal]]) -> tuple[Regime, ...]:
        return tuple(self.predict(row) for row in features)


def _fit_tree(
    rows: tuple[tuple[Decimal, ...], ...],
    labels: tuple[Regime, ...],
    indices: list[int],
    depth: int,
    max_depth: int,
    min_samples_split: int,
    max_features: int | None,
    rng: random.Random,
) -> _TreeNode:
    node_labels = [labels[index] for index in indices]
    majority = _majority(node_labels)
    if len(set(node_labels)) == 1 or depth >= max_depth or len(indices) < min_samples_split:
        return _TreeNode(label=majority)
    width = len(rows[0])
    feature_count = max_features if max_features is not None else max(1, int(sqrt(width)))
    feature_indices = rng.sample(range(width), min(feature_count, width))
    split = _best_split(rows, labels, indices, feature_indices)
    if split is None:
        return _TreeNode(label=majority)
    feature_index, threshold, left_indices, right_indices = split
    return _TreeNode(
        feature_index=feature_index,
        threshold=threshold,
        left=_fit_tree(rows, labels, left_indices, depth + 1, max_depth, min_samples_split, max_features, rng),
        right=_fit_tree(rows, labels, right_indices, depth + 1, max_depth, min_samples_split, max_features, rng),
    )


def _best_split(rows, labels, indices, feature_indices):
    best = None
    best_impurity = None
    for feature_index in feature_indices:
        values = sorted({rows[index][feature_index] for index in indices})
        for left_value, right_value in zip(values, values[1:]):
            threshold = (left_value + right_value) / Decimal("2")
            left = [index for index in indices if rows[index][feature_index] <= threshold]
            right = [index for index in indices if rows[index][feature_index] > threshold]
            if not left or not right:
                continue
            impurity = (len(left) * _gini([labels[i] for i in left]) + len(right) * _gini([labels[i] for i in right])) / len(indices)
            if best_impurity is None or impurity < best_impurity:
                best_impurity = impurity
                best = (feature_index, threshold, left, right)
    return best


def _gini(labels: list[Regime]) -> Decimal:
    total = Decimal(len(labels))
    return Decimal("1") - sum((Decimal(labels.count(label)) / total) ** 2 for label in set(labels))


def _majority(labels: list[Regime]) -> Regime:
    ordered = tuple(sorted(set(labels)))
    return min(ordered, key=lambda label: (-labels.count(label), ordered.index(label)))


def _predict_tree(node: _TreeNode, features: tuple[Decimal, ...]) -> Regime:
    if node.label is not None:
        return node.label
    if node.feature_index is None or node.threshold is None or node.left is None or node.right is None:
        raise ValueError("invalid fitted tree")
    return _predict_tree(node.left if features[node.feature_index] <= node.threshold else node.right, features)


def _tree_width(node: _TreeNode) -> int:
    if node.label is not None:
        return 0
    children = (node.left, node.right)
    widths = [_tree_width(child) for child in children if child is not None]
    return max(widths, default=0)


def _dot(left: Sequence[Decimal], right: Sequence[Decimal]) -> Decimal:
    return sum((a * b for a, b in zip(left, right)), Decimal("0"))


def _sigmoid(value: Decimal) -> Decimal:
    if value >= Decimal("60"):
        return Decimal("1")
    if value <= Decimal("-60"):
        return Decimal("0")
    return Decimal("1") / (Decimal("1") + (-value).exp())
