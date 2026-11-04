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
#ifndef MINDSPORE_CORE_OP_NAME_I_H_
#define MINDSPORE_CORE_OP_NAME_I_H_

namespace mindspore::ops {
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceSign = "InplaceSign";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInnerUnique = "InnerUnique";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceIndexCopy = "InplaceIndexCopy";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameImagView = "ImagView";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceIndexFillTensor = "InplaceIndexFillTensor";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceMaskedScatter = "InplaceMaskedScatter";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceSigmoid = "InplaceSigmoid";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceIndexFillScalar = "InplaceIndexFillScalar";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
