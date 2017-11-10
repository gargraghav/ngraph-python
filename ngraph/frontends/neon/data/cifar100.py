# ----------------------------------------------------------------------------
# Copyright 2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
import numpy as np
import os
from ngraph.util.persist import pickle_load, valid_path_append, fetch_file
import tarfile


class CIFAR100(object):
    """
    CIFAR100 data set from https://www.cs.toronto.edu/~kriz/cifar.html

    Arguments:
        path (str): Local path to copy data files.
    """

    def __init__(self, path='.'):
        self.path = path
        self.url = 'http://www.cs.toronto.edu/~kriz'
        self.filename = "cifar-100-python.tar.gz"
        self.size = 169001437

    def load_data(self):
        """
        Fetch the CIFAR-100 dataset and load it into memory.

        Arguments:
            path (str, optional): Local directory in which to cache the raw
                                  dataset.  Defaults to current directory.
            normalize (bool, optional): Whether to scale values between 0 and 1.
                                        Defaults to True.

        Returns:
            tuple: Both training and test sets are returned.
        """
        workdir, filepath = valid_path_append(self.path, '', self.filename)
        if not os.path.exists(filepath):
            fetch_file(self.url, self.filename, filepath, self.size)

        batchdir = os.path.join(workdir, 'cifar-100-python')
        if not os.path.exists(os.path.join(batchdir)):
            assert os.path.exists(filepath), "Must have cifar-100-python.tar.gz"
            with tarfile.open(filepath, 'r:gz') as f:
                f.extractall(workdir)

        train_batches = [os.path.join(batchdir, 'train')]
        Xlist, ylist = [], []
        for batch in train_batches:
            with open(batch, 'rb') as f:
                train_dict = pickle_load(f)
                Xlist.append(train_dict['data'])
                ylist.append(train_dict['coarse_labels'])

        X_train = np.vstack(Xlist).reshape(-1, 3, 32, 32)
        y_train = np.vstack(ylist).ravel()

        with open(os.path.join(batchdir, 'test'), 'rb') as f:
            test_dict = pickle_load(f)
            X_test, y_test = test_dict['data'], test_dict['coarse_labels']
            X_test = X_test.reshape(-1, 3, 32, 32)

        self.train_set = {'image': {'data': X_train,
                                    'axes': ('N', 'C', 'H', 'W')},
                          'label': {'data': y_train,
                                    'axes': ('N',)}}
        self.valid_set = {'image': {'data': X_test,
                                    'axes': ('N', 'C', 'H', 'W')},
                          'label': {'data': np.array(y_test),
                                    'axes': ('N',)}}

        return self.train_set, self.valid_set
