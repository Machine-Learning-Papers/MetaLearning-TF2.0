import os

import tensorflow as tf

from models.maml.maml import ModelAgnosticMetaLearningModel
from networks import SimpleModel, MiniImagenetModel
from tf_datasets import OmniglotDatabase, MiniImagenetDatabase


class UMTRA(ModelAgnosticMetaLearningModel):
    def __init__(
            self,
            database,
            network_cls,
            n,
            meta_batch_size,
            num_steps_ml,
            lr_inner_ml,
            num_steps_validation,
            save_after_epochs,
            augmentation_function=None
    ):
        self.augmentation_function = augmentation_function
        super(UMTRA, self).__init__(
            database=database,
            network_cls=network_cls,
            n=n,
            k=1,
            meta_batch_size=meta_batch_size,
            num_steps_ml=num_steps_ml,
            lr_inner_ml=lr_inner_ml,
            num_steps_validation=num_steps_validation,
            save_after_epochs=save_after_epochs,
        )

    def get_root(self):
        return os.path.dirname(__file__)

    def get_train_dataset(self):
        return self.database.get_umtra_dataset(
            self.database.train_folders,
            n=self.n,
            meta_batch_size=self.meta_batch_size,
            augmentation_function=self.augmentation_function
        )

    def get_config_info(self):
        return f'umtra_' \
               f'model-{self.network_cls.name}_' \
               f'mbs-{self.meta_batch_size}_' \
               f'n-{self.n}_' \
               f'k-{self.k}_' \
               f'stp-{self.num_steps_ml}'

def run_omniglot():
    omniglot_database = OmniglotDatabase(
        random_seed=-1,
        num_train_classes=1200,
        num_val_classes=100,
    )

    @tf.function
    def augment(images):
        result = list()
        for i in range(images.shape[0]):
            image = tf.image.flip_left_right(images[i, ...])
            result.append(image)

        return tf.stack(result)

    umtra = UMTRA(
        database=omniglot_database,
        network_cls=SimpleModel,
        n=5,
        meta_batch_size=32,
        num_steps_ml=5,
        lr_inner_ml=0.01,
        num_steps_validation=5,
        save_after_epochs=3,
        augmentation_function=augment
    )

    umtra.train(epochs=5)


def run_mini_imagenet():
    mini_imagenet_database = MiniImagenetDatabase(random_seed=-1)

    @tf.function
    def augment(images):
        result = list()
        for i in range(images.shape[0]):
            image = tf.image.flip_left_right(images[i, ...])
            result.append(image)

        return tf.stack(result)

    umtra = UMTRA(
        database=mini_imagenet_database,
        network_cls=MiniImagenetModel,
        n=5,
        meta_batch_size=8,
        num_steps_ml=5,
        lr_inner_ml=0.01,
        num_steps_validation=5,
        save_after_epochs=20,
        augmentation_function=augment
    )

    umtra.train(epochs=100)


if __name__ == '__main__':
    run_mini_imagenet()