import gpflow
import numpy as np

from gpflux.convolution import PatchHandler, ImagePatchConfig


def get_from_module(name, module):
    if hasattr(module, name):
        return name
    else:
        available = ' '.join([item for item in dir(module) if not item.startswith('__')])
        raise ValueError('{} not found. Available are {}'.format(name, available))


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def group_results(results):
    return np.array([result.history['loss'] for result in results]), \
           np.array([result.history['val_loss'] for result in results])


def labels_onehot_to_int(labels):
    return labels.argmax(axis=-1)[..., None].astype(np.int32)


def reshape_to_2d(x):
    return x.reshape(x.shape[0], -1)


def calc_multiclass_error(model, Xs, Ys, batchsize=100):
    Ns = len(Xs)
    splits = Ns // batchsize
    hits = []
    for xs, ys in zip(np.array_split(Xs, splits), np.array_split(Ys, splits)):
        logits, _ = model.predict_y(xs)
        acc = logits.argmax(1) == ys[:, 0]
        hits.append(acc)
    error = 1.0 - np.concatenate(hits, 0)
    return np.sum(error) * 100.0 / len(error)


def calc_avg_nll(model, x, y, batchsize=100):
    num_examples = x.shape[0]
    splits = num_examples // batchsize
    ll = 0
    for xs, ys in zip(np.array_split(x, splits), np.array_split(y, splits)):
        p, _ = model.predict_y(xs)
        p = ((ys == np.arange(10)[None, :]) * p).sum(-1)
        ll += np.log(p).sum()
    ll /= num_examples
    return -ll


class ImagePatchConfigCoder(gpflow.saver.coders.ObjectCoder):
    @classmethod
    def encoding_type(cls):
        return ImagePatchConfig


class PatchHandlerCoder(gpflow.saver.coders.ObjectCoder):
    @classmethod
    def encoding_type(cls):
        return PatchHandler


def save_gpflow_model(filename, model) -> None:
    context = gpflow.SaverContext(coders=[ImagePatchConfigCoder, PatchHandlerCoder])
    gpflow.Saver().save(filename, model, context=context)


def get_dataset_fraction(dataset, fraction):
    (train_features, train_targets), (test_features, test_targets) = dataset.load_data()
    seed = np.random.get_state()
    # fix the seed for numpy, so we always get the same fraction of examples
    np.random.seed(0)
    train_ind = np.random.permutation(range(train_features.shape[0]))[
                :int(train_features.shape[0] * fraction)]
    train_features, train_targets = train_features[train_ind], train_targets[train_ind]
    np.random.set_state(seed)
    return (train_features, train_targets), (test_features, test_targets)


def get_dataset_fixed_examples_per_class(dataset, num_examples):
    (train_features, train_targets), (test_features, test_targets) = dataset.load_data()
    selected_examples = []
    selected_targets = []
    num_classes = set(train_targets)
    for i in num_classes:
        indices = train_targets == i
        selected_examples.append(train_features[indices][:num_examples])
        selected_targets.append(train_targets[indices][:num_examples])
    selected_examples = np.vstack(selected_examples)
    selected_targets = np.hstack(selected_targets)
    return (selected_examples, selected_targets), (test_features, test_targets)
