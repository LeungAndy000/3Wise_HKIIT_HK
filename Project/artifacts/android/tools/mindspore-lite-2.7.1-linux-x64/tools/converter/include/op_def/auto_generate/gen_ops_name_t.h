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
#ifndef MINDSPORE_CORE_OP_NAME_T_H_
#define MINDSPORE_CORE_OP_NAME_T_H_

namespace mindspore::ops {
constexpr auto kNameTensorCopySlices = "TensorCopySlices";
constexpr auto kNameTriu = "Triu";
constexpr auto kNameTrunc = "Trunc";
constexpr auto kNameTExt = "TExt";
constexpr auto kNameTypeAs = "TypeAs";
constexpr auto kNameTraceV2Grad = "TraceV2Grad";
constexpr auto kNameTraceV2 = "TraceV2";
constexpr auto kNameTrilExt = "TrilExt";
constexpr auto kNameTrace = "Trace";
constexpr auto kNameToDtype = "ToDtype";
constexpr auto kNameThreshold = "Threshold";
constexpr auto kNameTake = "Take";
constexpr auto kNameTranspose = "Transpose";
constexpr auto kNameTanh = "Tanh";
constexpr auto kNameTanhGrad = "TanhGrad";
constexpr auto kNameTupleToTensor = "TupleToTensor";
constexpr auto kNameTopkExt = "TopkExt";
constexpr auto kNameToDevice = "ToDevice";
constexpr auto kNameTensorScatterElements = "TensorScatterElements";
constexpr auto kNameTile = "Tile";
constexpr auto kNameTopPRouter = "TopPRouter";
constexpr auto kNameTraceExt = "TraceExt";
constexpr auto kNameTan = "Tan";
constexpr auto kNameTensorShape = "TensorShape";
constexpr auto kNameTransposeExtView = "TransposeExtView";
constexpr auto kNameTransposeView = "TransposeView";
constexpr auto kNameThresholdGrad = "ThresholdGrad";
constexpr auto kNameToOther = "ToOther";
constexpr auto kNameTriangularSolve = "TriangularSolve";
constexpr auto kNameTupleToList = "TupleToList";
constexpr auto kNameTopKRouter = "TopKRouter";
constexpr auto kNameTransposeBatchMatmulTranspose = "TransposeBatchMatmulTranspose";
constexpr auto kNameTransData = "TransData";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_T_H_
