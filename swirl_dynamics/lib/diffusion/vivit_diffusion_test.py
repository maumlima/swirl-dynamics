# Copyright 2023 The swirl_dynamics Authors.
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

"""Tests for the light-weight ViViT Diffusion implementation."""
from absl.testing import absltest
from absl.testing import parameterized
import jax
import ml_collections
import numpy as np
from swirl_dynamics.lib.diffusion import vivit_diffusion


class VivitDiffusionTest(parameterized.TestCase):

  @parameterized.parameters(
      ((16, 32, 32), (2, 2, 2), 1),
      ((16, 64, 64), (4, 4, 4), 1,),
      ((32, 64, 64), (8, 8, 8), 2,),
  )
  def test_vivit_diffusion_output_shape(
      self, spatial_dims, patch_size, output_features
  ):
    batch, channels = 2, 3

    x = np.random.randn(batch, *spatial_dims, channels)
    sigma = np.linspace(0, 1, batch)

    config_patches = ml_collections.ConfigDict()
    config_patches.size = patch_size

    temporal_encoding_config = ml_collections.ConfigDict()
    temporal_encoding_config.method = "3d_conv"
    temporal_encoding_config.kernel_init_method = "central_frame_initializer"

    attention_config = ml_collections.ConfigDict()
    attention_config.type = "factorized_self_attention_block"
    attention_config.attention_order = "time_space"
    attention_config.attention_kernel_init_method = "xavier"

    vivit_model = vivit_diffusion.ViViTDiffusion(
        mlp_dim=4,
        num_layers=1,
        num_heads=1,
        output_features=output_features,
        patches=config_patches,
        hidden_size=6,
        temporal_encoding_config=temporal_encoding_config,
        attention_config=attention_config,
    )

    out, _ = vivit_model.init_with_output(
        jax.random.PRNGKey(42),
        x=x,
        sigma=sigma,
        is_training=False,
    )
    self.assertEqual(out.shape, (batch, *spatial_dims, output_features))


if __name__ == "__main__":
  absltest.main()