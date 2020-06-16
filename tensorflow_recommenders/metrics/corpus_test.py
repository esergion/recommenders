# Copyright 2020 The TensorFlow Recommenders Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint-as: python3
"""Tests corpus metrics."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

from tensorflow_recommenders import metrics


class CorpusTest(tf.test.TestCase):

  def test_factorized_top_k(self):

    rng = np.random.RandomState(42)

    num_candidates, num_queries, embedding_dim = (100, 10, 4)

    candidates = rng.normal(size=(num_candidates,
                                  embedding_dim)).astype(np.float32)
    query = rng.normal(size=(num_queries, embedding_dim)).astype(np.float32)
    true_candidates = rng.normal(size=(num_queries,
                                       embedding_dim)).astype(np.float32)

    positive_scores = (query * true_candidates).sum(axis=1, keepdims=True)
    candidate_scores = query @ candidates.T
    all_scores = np.concatenate([positive_scores, candidate_scores], axis=1)

    ks = [1, 5, 10, 50]

    metric = metrics.FactorizedTopK(
        candidates=tf.data.Dataset.from_tensor_slices(candidates).batch(32),
        metrics=[
            tf.keras.metrics.TopKCategoricalAccuracy(
                k=x, name=f"top_{x}_categorical_accuracy") for x in ks
        ],
        k=max(ks),
    )
    metric.update_state(
        query_embeddings=query, true_candidate_embeddings=true_candidates)

    for k, metric_value in zip(ks, metric.result()):
      in_top_k = tf.math.in_top_k(
          targets=np.zeros(num_queries).astype(np.int32),
          predictions=all_scores,
          k=k)

      self.assertAllClose(metric_value, in_top_k.numpy().mean())


if __name__ == "__main__":
  tf.test.main()
