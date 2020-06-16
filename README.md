# TensorFlow Recommenders

TensorFlow Recommenders is a library for building recommender system models
using TensorFlow.

It helps with the full workflow of building a recommender system, from data
preparation, model formulation, training, evaluation, to deployment.

It's built on Keras and aims to have a gentle learning curve while still giving
you the flexibility to build complex models.

## Installation

Install from `pip`:

```shell
pip install tensorflow-recommenders
```

## Quick start

Building a factorization model for the Movielens 100K dataset is very simple
([Colab](examples/quickstart.ipynb)):

```python
import tfrs

# Get the data.
ratings, movies = tfrs.datasets.movielens_100K()


# Build a model.
class Model(tfrs.Model):

  def __init__(self):
    super().__init__()

    # Set up user representation.
    self.user_model = tf.keras.layers.Embedding(
        input_dim=2000, output_dim=64)
    # Set up movie representation.
    self.item_model = tf.keras.layers.Embedding(
        input_dim=2000, output_dim=64)
    # Set up a retrieval task and evaluation metrics over the
    # entire dataset of candidates.
    self.task = tfrs.tasks.RetrievalTask(
        corpus_metrics=tfrs.metrics.FactorizedTopK(
            candidates=movies.batch(128).map(lambda x: self.item_model(x["movie_id"]))
        )
    )

  def train_loss(self, features: Dict[Text, tf.Tensor]) -> tf.Tensor:

    user_embeddings = self.user_model(features["user_id"])
    movie_embeddings = self.item_model(features["movie_id"])

    return self.task(user_embeddings, movie_embeddings)


model = Model()
model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

# Randomly shuffle data and split between train and test.
tf.random.set_seed(42)
shuffled = ratings.shuffle(100_000, seed=42, reshuffle_each_iteration=False)

train = shuffled.take(80_000)
test = shuffled.skip(80_000).take(20_000)

# Train.
model.fit(train.batch(4096), epochs=5)

# Evaluate.
model.evaluate(test.batch(4096), return_dict=True)
```

## Tutorials

-   [Quickstart](examples/tfrs_movielens.ipynb)
-   [Building a Movielens retrieval model](examples/tfrs_movielens.ipynb)
-   [Using context information](examples/movielens_side_information.ipynb)
-   [Multi-objective recommendations](examples/multitask.ipynb)
