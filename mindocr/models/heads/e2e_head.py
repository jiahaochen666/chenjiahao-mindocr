import mindspore.nn as nn
from mindspore import ops

from mindocr.models.utils.resnet_cells import ConvNormLayer


class PGNetHead(nn.Cell):
    """
    PGNet Head module for text detection.
    This module takes a single input feature map and applies convolutional operations
    to generate the output predicts.
    Args:
       in_channels (int): The feature dimension of a single feature map generated by the neck (E2eFpn).
    Returns:
       Tensor: The output predict of f_score, f_boder, f_char, f_direction.
    """
    def __init__(self, in_channels: int, **kwargs):
        super().__init__()
        character_dict_path = "./mindocr/utils/dict/ic15_dict.txt"
        with open(character_dict_path, "rb") as fin:
            lines = fin.readlines()
            character_length = len(lines) + 1

        self.relu = nn.ReLU()

        self.conv_f_score1 = ConvNormLayer(in_channels, 64, kernel_size=1, stride=1, act=True)
        self.conv_f_score2 = ConvNormLayer(64, 64, kernel_size=3, stride=1, padding=1, pad_mode="pad", act=True)
        self.conv_f_score3 = ConvNormLayer(64, 128, kernel_size=1, stride=1, act=True)

        self.conv1 = nn.Conv2d(128, 1, kernel_size=3, stride=1, padding=1, pad_mode="pad")

        self.conv_f_boder1 = ConvNormLayer(in_channels, 64, kernel_size=1, stride=1, act=True)
        self.conv_f_boder2 = ConvNormLayer(64, 64, kernel_size=3, stride=1, padding=1, pad_mode="pad", act=True)
        self.conv_f_boder3 = ConvNormLayer(64, 128, kernel_size=1, stride=1, act=True)

        self.conv2 = nn.Conv2d(128, 4, kernel_size=3, stride=1, padding=1, pad_mode="pad")

        self.conv_f_char1 = ConvNormLayer(in_channels, 128, kernel_size=1, stride=1, act=True)
        self.conv_f_char2 = ConvNormLayer(128, 128, kernel_size=3, stride=1, padding=1, pad_mode="pad", act=True)
        self.conv_f_char3 = ConvNormLayer(128, 256, kernel_size=1, stride=1, act=True)

        self.conv_f_char4 = ConvNormLayer(256, 256, kernel_size=3, stride=1, padding=1, pad_mode="pad", act=True)
        self.conv_f_char5 = ConvNormLayer(256, 256, kernel_size=1, stride=1, act=True)

        self.conv3 = nn.Conv2d(256, character_length, kernel_size=3, stride=1, padding=1, pad_mode="pad")

        self.conv_f_direc1 = ConvNormLayer(in_channels, 64, kernel_size=1, stride=1, act=True)
        self.conv_f_direc2 = ConvNormLayer(64, 64, kernel_size=3, stride=1, padding=1, pad_mode="pad", act=True)
        self.conv_f_direc3 = ConvNormLayer(64, 128, kernel_size=1, stride=1, act=True)

        self.conv4 = nn.Conv2d(128, 2, kernel_size=3, stride=1, padding=1, pad_mode="pad")

    def construct(self, x):
        # TCL Text Center Line
        f_score = self.conv_f_score1(x)
        f_score = self.conv_f_score2(f_score)
        f_score = self.conv_f_score3(f_score)
        f_score = self.conv1(f_score)
        f_score = ops.sigmoid(f_score)

        # TBO Text Order Offset
        f_border = self.conv_f_boder1(x)
        f_border = self.conv_f_boder2(f_border)
        f_border = self.conv_f_boder3(f_border)
        f_border = self.conv2(f_border)

        # TCC Text Character classification
        f_char = self.conv_f_char1(x)
        f_char = self.conv_f_char2(f_char)
        f_char = self.conv_f_char3(f_char)
        f_char = self.conv_f_char4(f_char)
        f_char = self.conv_f_char5(f_char)
        f_char = self.conv3(f_char)

        # TDO  Text Direction Offset
        f_direction = self.conv_f_direc1(x)
        f_direction = self.conv_f_direc2(f_direction)
        f_direction = self.conv_f_direc3(f_direction)
        f_direction = self.conv4(f_direction)

        predicts = {}
        predicts['f_score'] = f_score
        predicts['f_border'] = f_border
        predicts['f_char'] = f_char
        predicts['f_direction'] = f_direction
        return predicts