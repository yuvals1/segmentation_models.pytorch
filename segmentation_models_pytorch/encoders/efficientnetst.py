""" Each encoder should have following attributes and methods and be inherited from `_base.EncoderMixin`

Attributes:

    _out_channels (list of int): specify number of channels for each encoder feature tensor
    _depth (int): specify number of stages in decoder (in other words number of downsampling operations)
    _in_channels (int): default number of input channels in first Conv2d layer for encoder (usually 3)

Methods:

    forward(self, x: torch.Tensor)
        produce list of features of different spatial resolutions, each feature is a 4D torch.tensor of
        shape NCHW (features should be sorted in descending order according to spatial resolution, starting
        with resolution same as input `x` tensor).

        Input: `x` with shape (1, 3, 64, 64)
        Output: [f0, f1, f2, f3, f4, f5] - features with corresponding shapes
                [(1, 3, 64, 64), (1, 64, 32, 32), (1, 128, 16, 16), (1, 256, 8, 8),
                (1, 512, 4, 4), (1, 1024, 2, 2)] (C - dim may differ)

        also should support number of features according to specified depth, e.g. if depth = 5,
        number of feature tensors = 6 (one with same resolution as input and 5 downsampled),
        depth = 3 -> number of feature tensors = 4 (one with same resolution as input and 3 downsampled).
"""

from efficientnet_pytorch.utils import url_map, get_model_params
from .efficientnet import EfficientNetEncoder
from efficientnet_pytorch.model import get_same_padding_conv2d
from torch import nn


class EfficientNetSTEncoder(EfficientNetEncoder):
    def __init__(self, stage_idxs, out_channels, model_name, depth=5):
        super().__init__(stage_idxs, out_channels, model_name, depth)

    def forward(self, x):

        features = [self._swish(self._bn0_st(self._conv_stem_st(x)))]
        if self._depth > 0:
            x = self._swish(self._bn0(self._conv_stem(x)))
            features.append(x)

        if self._depth > 1:
            skip_connection_idx = 0
            for idx, block in enumerate(self._blocks):
                drop_connect_rate = self._global_params.drop_connect_rate
                if drop_connect_rate:
                    drop_connect_rate *= float(idx) / len(self._blocks)
                x = block(x, drop_connect_rate=drop_connect_rate)
                if idx == self._stage_idxs[skip_connection_idx] - 1:
                    skip_connection_idx += 1
                    features.append(x)
                    if skip_connection_idx + 1 == self._depth:
                        break

        return features

    def load_state_dict(self, state_dict, **kwargs):

        state_dict.pop("_fc.bias") if '_fc.bias' in state_dict.keys() else print('fc.bias not in dict')
        state_dict.pop("_fc.weight") if '_fc.weight' in state_dict.keys() else print('fc.weight not in dict')
        super().load_state_dict(state_dict, **kwargs)
        blocks_args, global_params = get_model_params('efficientnet-b0', override_params=None)
        Conv2d = get_same_padding_conv2d(image_size=global_params.image_size)

        self._conv_stem_st = Conv2d(3, 32, kernel_size=3, stride=1, bias=False)
        self._conv_stem_st.weight.data = self._conv_stem.weight.data

        bn_mom = 1 - global_params.batch_norm_momentum
        bn_eps = global_params.batch_norm_epsilon
        self._bn0_st = nn.BatchNorm2d(num_features=32, momentum=bn_mom, eps=bn_eps)


def _get_pretrained_settings(encoder):
    pretrained_settings = {
        "imagenet": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
            "url": url_map[encoder],
            "input_space": "RGB",
            "input_range": [0, 1],
        }
    }
    return pretrained_settings


efficient_netst_encoders = {
    "efficientnetst-b0": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b0"),
        "params": {
            "out_channels": (3, 32, 24, 40, 112, 320),
            "stage_idxs": (3, 5, 9),
            "model_name": "efficientnet-b0",
        },
    },
    "efficientnetst-b1": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b1"),
        "params": {
            "out_channels": (3, 32, 24, 40, 112, 320),
            "stage_idxs": (5, 8, 16),
            "model_name": "efficientnet-b1",
        },
    },
    "efficientnetst-b2": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b2"),
        "params": {
            "out_channels": (3, 32, 24, 48, 120, 352),
            "stage_idxs": (5, 8, 16),
            "model_name": "efficientnet-b2",
        },
    },
    "efficientnetst-b3": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b3"),
        "params": {
            "out_channels": (3, 40, 32, 48, 136, 384),
            "stage_idxs": (5, 8, 18),
            "model_name": "efficientnet-b3",
        },
    },
    "efficientnetst-b4": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b4"),
        "params": {
            "out_channels": (3, 48, 32, 56, 160, 448),
            "stage_idxs": (6, 10, 22),
            "model_name": "efficientnet-b4",
        },
    },
    "efficientnetst-b5": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b5"),
        "params": {
            "out_channels": (3, 48, 40, 64, 176, 512),
            "stage_idxs": (8, 13, 27),
            "model_name": "efficientnet-b5",
        },
    },
    "efficientnetst-b6": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b6"),
        "params": {
            "out_channels": (3, 56, 40, 72, 200, 576),
            "stage_idxs": (9, 15, 31),
            "model_name": "efficientnet-b6",
        },
    },
    "efficientnetst-b7": {
        "encoder": EfficientNetSTEncoder,
        "pretrained_settings": _get_pretrained_settings("efficientnet-b7"),
        "params": {
            "out_channels": (3, 64, 48, 80, 224, 640),
            "stage_idxs": (11, 18, 38),
            "model_name": "efficientnet-b7",
        },
    },
}
