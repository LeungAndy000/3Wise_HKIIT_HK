/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef MINDSPORE_CORE_OP_NAME_Q_H_
#define MINDSPORE_CORE_OP_NAME_Q_H_

namespace mindspore::ops {
constexpr auto kNameQr = "Qr";
constexpr auto kNameQuantMatmul = "QuantMatmul";
constexpr auto kNameQuantV2 = "QuantV2";
constexpr auto kNameQuantbatchmatmulSplitOut3 = "QuantbatchmatmulSplitOut3";
constexpr auto kNameQMatmulSplitSiluFastgeluAddMulOut1 = "QMatmulSplitSiluFastgeluAddMulOut1";
constexpr auto kNameQuantbatchmatmulSplitSiluOut2 = "QuantbatchmatmulSplitSiluOut2";
constexpr auto kNameQuantbatchmatmulSplitOut2 = "QuantbatchmatmulSplitOut2";
constexpr auto kNameQuantBatchMatmul = "QuantBatchMatmul";
constexpr auto kNameQuantLinearSparse = "QuantLinearSparse";
constexpr auto kNameQMatmulSplitSiluMulOut1 = "QMatmulSplitSiluMulOut1";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_Q_H_
