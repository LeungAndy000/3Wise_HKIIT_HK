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
#ifndef MINDSPORE_CORE_OPS_GEN_LITE_OPS_H_
#define MINDSPORE_CORE_OPS_GEN_LITE_OPS_H_

#include <vector>
#include "ops/base_operator.h"

namespace mindspore::ops {
class OPS_API CdistGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CdistGrad);
  CdistGrad();
  
    void set_p(const float &p);
    float get_p() const;
};

class OPS_API BatchNormWithAddAndActivation : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormWithAddAndActivation);
  BatchNormWithAddAndActivation();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_momentum(const float &momentum);
    float get_momentum() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API NewEmpty : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NewEmpty);
  NewEmpty();

};

class OPS_API CumProd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CumProd);
  CumProd();
  
    void set_exclusive(const bool &exclusive);
    bool get_exclusive() const;
    void set_reverse(const bool &reverse);
    bool get_reverse() const;
};

class OPS_API ReplicationPad3DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad3DGrad);
  ReplicationPad3DGrad();

};

class OPS_API AvgPool1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool1D);
  AvgPool1D();

};

class OPS_API ExpandDims : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ExpandDims);
  ExpandDims();

};

class OPS_API MaskedSelectGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaskedSelectGrad);
  MaskedSelectGrad();

};

class OPS_API UpsampleBicubic2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleBicubic2D);
  UpsampleBicubic2D();

};

class OPS_API InplaceLog : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceLog);
  InplaceLog();

};

class OPS_API ConvTranspose2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ConvTranspose2D);
  ConvTranspose2D();

};

class OPS_API InplaceAddmm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceAddmm);
  InplaceAddmm();

};

class OPS_API ReduceMean : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceMean);
  ReduceMean();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API CeLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CeLU);
  CeLU();
  
    void set_alpha(const float &alpha);
    float get_alpha() const;
};

class OPS_API IFFTShift : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IFFTShift);
  IFFTShift();

};

class OPS_API BCEWithLogitsLoss : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BCEWithLogitsLoss);
  BCEWithLogitsLoss();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API Conj : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conj);
  Conj();

};

class OPS_API IncreFlashAttention : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IncreFlashAttention);
  IncreFlashAttention();
  
    void set_num_heads(const int64_t &num_heads);
    int64_t get_num_heads() const;
    void set_input_layout(const int64_t &input_layout);
    int64_t get_input_layout() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_num_key_value_heads(const int64_t &num_key_value_heads);
    int64_t get_num_key_value_heads() const;
    void set_block_size(const int64_t &block_size);
    int64_t get_block_size() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
};

class OPS_API AddScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddScalar);
  AddScalar();

};

class OPS_API LstsqV2Grad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LstsqV2Grad);
  LstsqV2Grad();

};

class OPS_API Add : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Add);
  Add();

};

class OPS_API InplaceGroupedMatmulAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceGroupedMatmulAdd);
  InplaceGroupedMatmulAdd();

};

class OPS_API DropoutGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DropoutGradExt);
  DropoutGradExt();

};

class OPS_API ApplyCamePart2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyCamePart2);
  ApplyCamePart2();

};

class OPS_API BatchNormGradWithAddAndActivation : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGradWithAddAndActivation);
  BatchNormGradWithAddAndActivation();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API InplaceMatmulAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMatmulAdd);
  InplaceMatmulAdd();

};

class OPS_API DCTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DCTN);
  DCTN();

};

class OPS_API XLogYScalarOther : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(XLogYScalarOther);
  XLogYScalarOther();

};

class OPS_API ApplyCamePart4 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyCamePart4);
  ApplyCamePart4();

};

class OPS_API ReLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReLU);
  ReLU();

};

class OPS_API Norm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Norm);
  Norm();

};

class OPS_API MSELossGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MSELossGradExt);
  MSELossGradExt();

};

class OPS_API Cast : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cast);
  Cast();

};

class OPS_API InplaceMuls : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMuls);
  InplaceMuls();

};

class OPS_API UpsampleTrilinear3DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleTrilinear3DGrad);
  UpsampleTrilinear3DGrad();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
};

class OPS_API TensorCopySlices : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TensorCopySlices);
  TensorCopySlices();

};

class OPS_API Triu : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Triu);
  Triu();
  
    void set_diagonal(const int64_t &diagonal);
    int64_t get_diagonal() const;
};

class OPS_API MishGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MishGradExt);
  MishGradExt();

};

class OPS_API BitwiseXorTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseXorTensor);
  BitwiseXorTensor();

};

class OPS_API MedianExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MedianExt);
  MedianExt();

};

class OPS_API FFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFT2);
  FFT2();

};

class OPS_API UpsampleLinear1DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleLinear1DGrad);
  UpsampleLinear1DGrad();

};

class OPS_API InplaceSubScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceSubScalar);
  InplaceSubScalar();

};

class OPS_API MoeDistributeCombine : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeDistributeCombine);
  MoeDistributeCombine();

};

class OPS_API Mm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Mm);
  Mm();

};

class OPS_API MaximumGradGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaximumGradGrad);
  MaximumGradGrad();
  
    void set_grad_x(const bool &grad_x);
    bool get_grad_x() const;
    void set_grad_y(const bool &grad_y);
    bool get_grad_y() const;
};

class OPS_API SplitTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SplitTensor);
  SplitTensor();

};

class OPS_API NLLLoss2d : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NLLLoss2d);
  NLLLoss2d();

};

class OPS_API SoftplusExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftplusExt);
  SoftplusExt();

};

class OPS_API GroupNormGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupNormGrad);
  GroupNormGrad();

};

class OPS_API Atanh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Atanh);
  Atanh();

};

class OPS_API BitwiseXorScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseXorScalar);
  BitwiseXorScalar();

};

class OPS_API Minimum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Minimum);
  Minimum();

};

class OPS_API OnesLikeExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(OnesLikeExt);
  OnesLikeExt();

};

class OPS_API FloorDivScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FloorDivScalar);
  FloorDivScalar();

};

class OPS_API Trunc : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Trunc);
  Trunc();

};

class OPS_API InplaceClampTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceClampTensor);
  InplaceClampTensor();

};

class OPS_API RealDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RealDiv);
  RealDiv();

};

class OPS_API Reciprocal : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Reciprocal);
  Reciprocal();

};

class OPS_API TExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TExt);
  TExt();

};

class OPS_API FmodScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FmodScalar);
  FmodScalar();

};

class OPS_API Dropout : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Dropout);
  Dropout();
  
    void set_keep_prob(const float &keep_prob);
    float get_keep_prob() const;
    void set_Seed0(const int64_t &Seed0);
    int64_t get_Seed0() const;
    void set_Seed1(const int64_t &Seed1);
    int64_t get_Seed1() const;
};

class OPS_API InplaceClampScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceClampScalar);
  InplaceClampScalar();

};

class OPS_API ReplicationPad3D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad3D);
  ReplicationPad3D();

};

class OPS_API InplaceSiLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceSiLU);
  InplaceSiLU();

};

class OPS_API NewFull : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NewFull);
  NewFull();

};

class OPS_API TypeAs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TypeAs);
  TypeAs();

};

class OPS_API ConvolutionGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ConvolutionGrad);
  ConvolutionGrad();

};

class OPS_API TraceV2Grad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TraceV2Grad);
  TraceV2Grad();

};

class OPS_API BiasAddGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BiasAddGrad);
  BiasAddGrad();
  
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API SiLUGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SiLUGrad);
  SiLUGrad();

};

class OPS_API BincountExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BincountExt);
  BincountExt();

};

class OPS_API IRFFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IRFFT2);
  IRFFT2();

};

class OPS_API LeakyReLUGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LeakyReLUGradExt);
  LeakyReLUGradExt();

};

class OPS_API LayerNormGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormGradExt);
  LayerNormGradExt();

};

class OPS_API MinDim : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MinDim);
  MinDim();

};

class OPS_API BatchNormGradGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGradGrad);
  BatchNormGradGrad();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API StackExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(StackExt);
  StackExt();
  
    void set_dim(const int64_t &dim);
    int64_t get_dim() const;
};

class OPS_API UniqueConsecutive : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UniqueConsecutive);
  UniqueConsecutive();
  
    void set_return_inverse(const bool &return_inverse);
    bool get_return_inverse() const;
    void set_return_counts(const bool &return_counts);
    bool get_return_counts() const;
    void set_dim(const int64_t &dim);
    int64_t get_dim() const;
};

class OPS_API Conv1DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv1DExt);
  Conv1DExt();

};

class OPS_API Eye : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Eye);
  Eye();

};

class OPS_API ScalarEq : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarEq);
  ScalarEq();

};

class OPS_API AdaptiveAvgPool1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveAvgPool1D);
  AdaptiveAvgPool1D();

};

class OPS_API HistcExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HistcExt);
  HistcExt();

};

class OPS_API AddLayerNormGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddLayerNormGrad);
  AddLayerNormGrad();

};

class OPS_API ScalarUadd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarUadd);
  ScalarUadd();

};

class OPS_API KLDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(KLDiv);
  KLDiv();

};

class OPS_API InplaceScatterSrcReduce : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceScatterSrcReduce);
  InplaceScatterSrcReduce();

};

class OPS_API FFTShapeCopy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTShapeCopy);
  FFTShapeCopy();

};

class OPS_API InplaceDivs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceDivs);
  InplaceDivs();

};

class OPS_API BinaryCrossEntropyWithLogitsBackward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BinaryCrossEntropyWithLogitsBackward);
  BinaryCrossEntropyWithLogitsBackward();

};

class OPS_API AtanExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AtanExt);
  AtanExt();

};

class OPS_API CholeskyInverse : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CholeskyInverse);
  CholeskyInverse();
  
    void set_upper(const bool &upper);
    bool get_upper() const;
};

class OPS_API Arange : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Arange);
  Arange();

};

class OPS_API ScalarFloorDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarFloorDiv);
  ScalarFloorDiv();

};

class OPS_API NonZero : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NonZero);
  NonZero();

};

class OPS_API SequenceConcat : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SequenceConcat);
  SequenceConcat();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API Max : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Max);
  Max();

};

class OPS_API LessEqual : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LessEqual);
  LessEqual();

};

class OPS_API TraceV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TraceV2);
  TraceV2();

};

class OPS_API Dot : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Dot);
  Dot();

};

class OPS_API Roll : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Roll);
  Roll();
  
    void set_shifts(const std::vector<int64_t> &shifts);
    std::vector<int64_t> get_shifts() const;
    void set_dims(const std::vector<int64_t> &dims);
    std::vector<int64_t> get_dims() const;
};

class OPS_API InnerNonZero : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerNonZero);
  InnerNonZero();

};

class OPS_API Assign : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Assign);
  Assign();

};

class OPS_API ReflectionPad2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad2DGrad);
  ReflectionPad2DGrad();

};

class OPS_API UpsampleTrilinear3D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleTrilinear3D);
  UpsampleTrilinear3D();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
};

class OPS_API Cholesky : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cholesky);
  Cholesky();
  
    void set_upper(const bool &upper);
    bool get_upper() const;
};

class OPS_API TrilExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TrilExt);
  TrilExt();

};

class OPS_API Cdist : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cdist);
  Cdist();
  
    void set_p(const float &p);
    float get_p() const;
};

class OPS_API InplaceFillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFillScalar);
  InplaceFillScalar();

};

class OPS_API AllFinite : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AllFinite);
  AllFinite();

};

class OPS_API HSigmoidGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HSigmoidGrad);
  HSigmoidGrad();

};

class OPS_API GridSampler3DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GridSampler3DGrad);
  GridSampler3DGrad();
  
    void set_interpolation_mode(const int64_t &interpolation_mode);
    int64_t get_interpolation_mode() const;
    void set_padding_mode(const int64_t &padding_mode);
    int64_t get_padding_mode() const;
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_output_mask(const std::vector<int64_t> &output_mask);
    std::vector<int64_t> get_output_mask() const;
};

class OPS_API AcosExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AcosExt);
  AcosExt();

};

class OPS_API CellBackwardHook : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CellBackwardHook);
  CellBackwardHook();

};

class OPS_API RotaryPositionEmbeddingGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RotaryPositionEmbeddingGrad);
  RotaryPositionEmbeddingGrad();

};

class OPS_API AsinhGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AsinhGrad);
  AsinhGrad();

};

class OPS_API Im2ColExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Im2ColExt);
  Im2ColExt();

};

class OPS_API IRFFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IRFFT);
  IRFFT();

};

class OPS_API Diagonal : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Diagonal);
  Diagonal();
  
    void set_offset(const int64_t &offset);
    int64_t get_offset() const;
    void set_dim1(const int64_t &dim1);
    int64_t get_dim1() const;
    void set_dim2(const int64_t &dim2);
    int64_t get_dim2() const;
};

class OPS_API ReplicationPad1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad1D);
  ReplicationPad1D();

};

class OPS_API InplaceErfinv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceErfinv);
  InplaceErfinv();

};

class OPS_API AsStrided : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AsStrided);
  AsStrided();

};

class OPS_API SolveTriangular : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SolveTriangular);
  SolveTriangular();

};

class OPS_API Squeeze : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Squeeze);
  Squeeze();
  
    void set_axis(const std::vector<int64_t> &axis);
    std::vector<int64_t> get_axis() const;
};

class OPS_API ScalarLe : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarLe);
  ScalarLe();

};

class OPS_API Conv3DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv3DExt);
  Conv3DExt();

};

class OPS_API BatchMatMulExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchMatMulExt);
  BatchMatMulExt();

};

class OPS_API SelectV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SelectV2);
  SelectV2();

};

class OPS_API SoftMarginLossGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftMarginLossGrad);
  SoftMarginLossGrad();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API AdaptiveMaxPool2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveMaxPool2D);
  AdaptiveMaxPool2D();
  
    void set_output_size(const std::vector<int64_t> &output_size);
    std::vector<int64_t> get_output_size() const;
};

class OPS_API Addbmm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Addbmm);
  Addbmm();

};

class OPS_API BatchNormStats : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormStats);
  BatchNormStats();

};

class OPS_API ReduceAll : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceAll);
  ReduceAll();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API Trace : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Trace);
  Trace();

};

class OPS_API ScalarLt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarLt);
  ScalarLt();

};

class OPS_API FullLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FullLike);
  FullLike();

};

class OPS_API ReflectionPad3D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad3D);
  ReflectionPad3D();

};

class OPS_API BroadcastToView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BroadcastToView);
  BroadcastToView();

};

class OPS_API BroadcastTo : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BroadcastTo);
  BroadcastTo();
  
    void set_shape(const std::vector<int64_t> &shape);
    std::vector<int64_t> get_shape() const;
};

class OPS_API AdaptiveAvgPool3DGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveAvgPool3DGradExt);
  AdaptiveAvgPool3DGradExt();

};

class OPS_API AddcmulExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddcmulExt);
  AddcmulExt();

};

class OPS_API GatherD : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GatherD);
  GatherD();

};

class OPS_API Expm1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Expm1);
  Expm1();

};

class OPS_API MatrixInverseExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatrixInverseExt);
  MatrixInverseExt();

};

class OPS_API Sign : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sign);
  Sign();

};

class OPS_API NLLLossGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NLLLossGrad);
  NLLLossGrad();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
    void set_ignore_index(const int64_t &ignore_index);
    int64_t get_ignore_index() const;
};

class OPS_API IFFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IFFT);
  IFFT();

};

class OPS_API Angle : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Angle);
  Angle();

};

class OPS_API ExpandAs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ExpandAs);
  ExpandAs();

};

class OPS_API HSwishGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HSwishGrad);
  HSwishGrad();

};

class OPS_API InplaceMul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMul);
  InplaceMul();

};

class OPS_API FFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTN);
  FFTN();

};

class OPS_API BitwiseNot : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseNot);
  BitwiseNot();

};

class OPS_API AdamW : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdamW);
  AdamW();

};

class OPS_API FlattenExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FlattenExt);
  FlattenExt();

};

class OPS_API RFFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RFFT2);
  RFFT2();

};

class OPS_API KLDivGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(KLDivGrad);
  KLDivGrad();

};

class OPS_API LogicalXor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogicalXor);
  LogicalXor();

};

class OPS_API LayerNormGradGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormGradGrad);
  LayerNormGradGrad();
  
    void set_begin_norm_axis(const int64_t &begin_norm_axis);
    int64_t get_begin_norm_axis() const;
    void set_begin_params_axis(const int64_t &begin_params_axis);
    int64_t get_begin_params_axis() const;
};

class OPS_API ScatterNd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScatterNd);
  ScatterNd();

};

class OPS_API InplaceSign : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceSign);
  InplaceSign();

};

class OPS_API RFFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RFFTN);
  RFFTN();

};

class OPS_API InplaceFloorDivide : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFloorDivide);
  InplaceFloorDivide();

};

class OPS_API Slice : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Slice);
  Slice();

};

class OPS_API LogAddExp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogAddExp);
  LogAddExp();

};

class OPS_API RingAttentionUpdate : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RingAttentionUpdate);
  RingAttentionUpdate();

};

class OPS_API AvgPool2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool2DGrad);
  AvgPool2DGrad();

};

class OPS_API IHFFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IHFFTN);
  IHFFTN();

};

class OPS_API ReflectionPad1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad1D);
  ReflectionPad1D();

};

class OPS_API FFTWithSize : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTWithSize);
  FFTWithSize();
  
    void set_signal_ndim(const int64_t &signal_ndim);
    int64_t get_signal_ndim() const;
    void set_inverse(const bool &inverse);
    bool get_inverse() const;
    void set_real(const bool &real);
    bool get_real() const;
    void set_norm(const int64_t &norm);
    int64_t get_norm() const;
    void set_onesided(const bool &onesided);
    bool get_onesided() const;
    void set_signal_sizes(const std::vector<int64_t> &signal_sizes);
    std::vector<int64_t> get_signal_sizes() const;
};

class OPS_API Copy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Copy);
  Copy();

};

class OPS_API Std : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Std);
  Std();

};

class OPS_API HShrinkGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HShrinkGrad);
  HShrinkGrad();
  
    void set_lambd(const float &lambd);
    float get_lambd() const;
};

class OPS_API RepeatInterleaveInt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RepeatInterleaveInt);
  RepeatInterleaveInt();

};

class OPS_API Empty : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Empty);
  Empty();

};

class OPS_API NanToNum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NanToNum);
  NanToNum();
  
    void set_nan(const float &nan);
    float get_nan() const;
    void set_posinf(const float &posinf);
    float get_posinf() const;
    void set_neginf(const float &neginf);
    float get_neginf() const;
};

class OPS_API SoftMarginLoss : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftMarginLoss);
  SoftMarginLoss();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API MedianDim : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MedianDim);
  MedianDim();

};

class OPS_API ScatterValue : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScatterValue);
  ScatterValue();

};

class OPS_API Sigmoid : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sigmoid);
  Sigmoid();

};

class OPS_API AvgPool : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool);
  AvgPool();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pad_mode(const int64_t &pad_mode);
    int64_t get_pad_mode() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API Cross : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cross);
  Cross();
  
    void set_dim(const int64_t &dim);
    int64_t get_dim() const;
};

class OPS_API ScalarLog : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarLog);
  ScalarLog();

};

class OPS_API GroupTopk : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupTopk);
  GroupTopk();

};

class OPS_API AddLayerNormV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddLayerNormV2);
  AddLayerNormV2();

};

class OPS_API ListToTuple : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ListToTuple);
  ListToTuple();

};

class OPS_API ZerosLikeExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ZerosLikeExt);
  ZerosLikeExt();

};

class OPS_API ToDtype : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ToDtype);
  ToDtype();

};

class OPS_API ExtractImagePatches : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ExtractImagePatches);
  ExtractImagePatches();
  
    void set_ksizes(const std::vector<int64_t> &ksizes);
    std::vector<int64_t> get_ksizes() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_rates(const std::vector<int64_t> &rates);
    std::vector<int64_t> get_rates() const;
    void set_padding(const int64_t &padding);
    int64_t get_padding() const;
};

class OPS_API RemainderTensorScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RemainderTensorScalar);
  RemainderTensorScalar();

};

class OPS_API InplaceAddsExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceAddsExt);
  InplaceAddsExt();

};

class OPS_API Erfinv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Erfinv);
  Erfinv();

};

class OPS_API RandInt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandInt);
  RandInt();

};

class OPS_API EluExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EluExt);
  EluExt();
  
    void set_alpha(const float &alpha);
    float get_alpha() const;
};

class OPS_API Div : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Div);
  Div();

};

class OPS_API ReflectionPad3DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad3DGrad);
  ReflectionPad3DGrad();

};

class OPS_API Threshold : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Threshold);
  Threshold();

};

class OPS_API Log : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Log);
  Log();

};

class OPS_API Exp2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Exp2);
  Exp2();

};

class OPS_API Mv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Mv);
  Mv();

};

class OPS_API Chunk : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Chunk);
  Chunk();

};

class OPS_API LinalgQr : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LinalgQr);
  LinalgQr();

};

class OPS_API EmbeddingDenseBackward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EmbeddingDenseBackward);
  EmbeddingDenseBackward();

};

class OPS_API Conv2DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv2DExt);
  Conv2DExt();

};

class OPS_API ResizeD : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeD);
  ResizeD();

};

class OPS_API LogSumExp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSumExp);
  LogSumExp();

};

class OPS_API InplaceScatterValue : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceScatterValue);
  InplaceScatterValue();

};

class OPS_API RandLikeExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandLikeExt);
  RandLikeExt();

};

class OPS_API RepeatInterleaveTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RepeatInterleaveTensor);
  RepeatInterleaveTensor();

};

class OPS_API Real : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Real);
  Real();

};

class OPS_API DropoutExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DropoutExt);
  DropoutExt();

};

class OPS_API Concat : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Concat);
  Concat();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API Sub : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sub);
  Sub();

};

class OPS_API MSELossExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MSELossExt);
  MSELossExt();

};

class OPS_API Polar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Polar);
  Polar();

};

class OPS_API MoeTokenPermuteGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeTokenPermuteGrad);
  MoeTokenPermuteGrad();

};

class OPS_API InnerUnique : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerUnique);
  InnerUnique();

};

class OPS_API View : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(View);
  View();

};

class OPS_API MaskedFill : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaskedFill);
  MaskedFill();

};

class OPS_API CustomExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CustomExt);
  CustomExt();

};

class OPS_API BatchNormGradWithActivation : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGradWithActivation);
  BatchNormGradWithActivation();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API SplitWithSizeView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SplitWithSizeView);
  SplitWithSizeView();

};

class OPS_API ResizeNearestNeighbor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeNearestNeighbor);
  ResizeNearestNeighbor();
  
    void set_size(const std::vector<int64_t> &size);
    std::vector<int64_t> get_size() const;
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API FlashAttentionScore : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FlashAttentionScore);
  FlashAttentionScore();
  
    void set_head_num(const int64_t &head_num);
    int64_t get_head_num() const;
    void set_keep_prob(const float &keep_prob);
    float get_keep_prob() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_pre_tokens(const int64_t &pre_tokens);
    int64_t get_pre_tokens() const;
    void set_next_tokens(const int64_t &next_tokens);
    int64_t get_next_tokens() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
    void set_input_layout(const int64_t &input_layout);
    int64_t get_input_layout() const;
    void set_sparse_mode(const int64_t &sparse_mode);
    int64_t get_sparse_mode() const;
};

class OPS_API BatchNormExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormExt);
  BatchNormExt();

};

class OPS_API Qr : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Qr);
  Qr();
  
    void set_full_matrices(const bool &full_matrices);
    bool get_full_matrices() const;
};

class OPS_API InplaceIndexAddExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceIndexAddExt);
  InplaceIndexAddExt();

};

class OPS_API HShrink : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HShrink);
  HShrink();
  
    void set_lambd(const float &lambd);
    float get_lambd() const;
};

class OPS_API GreaterEqual : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GreaterEqual);
  GreaterEqual();

};

class OPS_API Eig : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Eig);
  Eig();
  
    void set_compute_v(const bool &compute_v);
    bool get_compute_v() const;
};

class OPS_API LogSoftmaxGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSoftmaxGrad);
  LogSoftmaxGrad();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API Asin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Asin);
  Asin();

};

class OPS_API IDCTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IDCTN);
  IDCTN();

};

class OPS_API InplaceFloor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFloor);
  InplaceFloor();

};

class OPS_API Argmax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Argmax);
  Argmax();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_output_type(const int64_t &output_type);
    int64_t get_output_type() const;
};

class OPS_API ApplyAdamW : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyAdamW);
  ApplyAdamW();

};

class OPS_API RFFTFreq : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RFFTFreq);
  RFFTFreq();

};

class OPS_API L1LossBackwardExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(L1LossBackwardExt);
  L1LossBackwardExt();

};

class OPS_API ScalarBool : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarBool);
  ScalarBool();

};

class OPS_API Take : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Take);
  Take();

};

class OPS_API LayerNormExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormExt);
  LayerNormExt();

};

class OPS_API BinaryCrossEntropy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BinaryCrossEntropy);
  BinaryCrossEntropy();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API ResizeLinear1DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeLinear1DGrad);
  ResizeLinear1DGrad();
  
    void set_coordinate_transformation_mode(const int64_t &coordinate_transformation_mode);
    int64_t get_coordinate_transformation_mode() const;
};

class OPS_API Cosh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cosh);
  Cosh();

};

class OPS_API ChunkView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ChunkView);
  ChunkView();

};

class OPS_API LogMatrixDeterminant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogMatrixDeterminant);
  LogMatrixDeterminant();

};

class OPS_API GridSampler3D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GridSampler3D);
  GridSampler3D();
  
    void set_interpolation_mode(const int64_t &interpolation_mode);
    int64_t get_interpolation_mode() const;
    void set_padding_mode(const int64_t &padding_mode);
    int64_t get_padding_mode() const;
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
};

class OPS_API Generator : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Generator);
  Generator();

};

class OPS_API Baddbmm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Baddbmm);
  Baddbmm();

};

class OPS_API InplaceMaskedFillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMaskedFillScalar);
  InplaceMaskedFillScalar();

};

class OPS_API BiasAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BiasAdd);
  BiasAdd();
  
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API AsinhExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AsinhExt);
  AsinhExt();

};

class OPS_API LogSoftmaxExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSoftmaxExt);
  LogSoftmaxExt();

};

class OPS_API Meshgrid : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Meshgrid);
  Meshgrid();
  
    void set_indexing(const int64_t &indexing);
    int64_t get_indexing() const;
};

class OPS_API ResizeBilinearGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeBilinearGrad);
  ResizeBilinearGrad();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API NormalFloatTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NormalFloatTensor);
  NormalFloatTensor();

};

class OPS_API UpsampleNearest3DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest3DGrad);
  UpsampleNearest3DGrad();

};

class OPS_API ScalarSub : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarSub);
  ScalarSub();

};

class OPS_API AddExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddExt);
  AddExt();

};

class OPS_API Addcmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Addcmul);
  Addcmul();

};

class OPS_API Sinc : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sinc);
  Sinc();

};

class OPS_API RandpermExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandpermExt);
  RandpermExt();

};

class OPS_API ViewAs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ViewAs);
  ViewAs();

};

class OPS_API NormalTensorTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NormalTensorTensor);
  NormalTensorTensor();

};

class OPS_API Logit : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Logit);
  Logit();
  
    void set_eps(const float &eps);
    float get_eps() const;
};

class OPS_API Col2ImExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Col2ImExt);
  Col2ImExt();

};

class OPS_API ResizeBicubic : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeBicubic);
  ResizeBicubic();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API DiagExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DiagExt);
  DiagExt();

};

class OPS_API MaxPoolGradWithIndices : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxPoolGradWithIndices);
  MaxPoolGradWithIndices();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pads(const std::vector<int64_t> &pads);
    std::vector<int64_t> get_pads() const;
    void set_dilation(const std::vector<int64_t> &dilation);
    std::vector<int64_t> get_dilation() const;
    void set_ceil_mode(const bool &ceil_mode);
    bool get_ceil_mode() const;
    void set_argmax_type(const int64_t &argmax_type);
    int64_t get_argmax_type() const;
};

class OPS_API InplaceBernoulliScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceBernoulliScalar);
  InplaceBernoulliScalar();

};

class OPS_API MaxPoolWithMask : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxPoolWithMask);
  MaxPoolWithMask();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pads(const std::vector<int64_t> &pads);
    std::vector<int64_t> get_pads() const;
    void set_dilation(const std::vector<int64_t> &dilation);
    std::vector<int64_t> get_dilation() const;
    void set_ceil_mode(const bool &ceil_mode);
    bool get_ceil_mode() const;
    void set_argmax_type(const int64_t &argmax_type);
    int64_t get_argmax_type() const;
};

class OPS_API IFFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IFFT2);
  IFFT2();

};

class OPS_API Mul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Mul);
  Mul();

};

class OPS_API Square : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Square);
  Square();

};

class OPS_API MishExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MishExt);
  MishExt();

};

class OPS_API Select : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Select);
  Select();

};

class OPS_API RsqrtGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RsqrtGrad);
  RsqrtGrad();

};

class OPS_API FFNExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFNExt);
  FFNExt();
  
    void set_activation(const int64_t &activation);
    int64_t get_activation() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
};

class OPS_API Correlate : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Correlate);
  Correlate();
  
    void set_pad_mode(const int64_t &pad_mode);
    int64_t get_pad_mode() const;
};

class OPS_API GenerateEodMaskV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GenerateEodMaskV2);
  GenerateEodMaskV2();

};

class OPS_API Log2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Log2);
  Log2();

};

class OPS_API MaskedScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaskedScatter);
  MaskedScatter();

};

class OPS_API InplaceIndexCopy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceIndexCopy);
  InplaceIndexCopy();

};

class OPS_API Transpose : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Transpose);
  Transpose();

};

class OPS_API PromptFlashAttention : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PromptFlashAttention);
  PromptFlashAttention();
  
    void set_num_heads(const int64_t &num_heads);
    int64_t get_num_heads() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_pre_tokens(const int64_t &pre_tokens);
    int64_t get_pre_tokens() const;
    void set_next_tokens(const int64_t &next_tokens);
    int64_t get_next_tokens() const;
    void set_input_layout(const int64_t &input_layout);
    int64_t get_input_layout() const;
    void set_num_key_value_heads(const int64_t &num_key_value_heads);
    int64_t get_num_key_value_heads() const;
    void set_sparse_mode(const int64_t &sparse_mode);
    int64_t get_sparse_mode() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
};

class OPS_API OnesLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(OnesLike);
  OnesLike();

};

class OPS_API Tanh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Tanh);
  Tanh();

};

class OPS_API AtanGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AtanGrad);
  AtanGrad();

};

class OPS_API ApplyCamePart1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyCamePart1);
  ApplyCamePart1();

};

class OPS_API DropoutGenMaskExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DropoutGenMaskExt);
  DropoutGenMaskExt();

};

class OPS_API GatherDGradV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GatherDGradV2);
  GatherDGradV2();

};

class OPS_API RemainderTensorTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RemainderTensorTensor);
  RemainderTensorTensor();

};

class OPS_API ResizeBicubicGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeBicubicGrad);
  ResizeBicubicGrad();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API TanhGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TanhGrad);
  TanhGrad();

};

class OPS_API IHFFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IHFFT2);
  IHFFT2();

};

class OPS_API StdMean : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(StdMean);
  StdMean();

};

class OPS_API SearchSorted : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SearchSorted);
  SearchSorted();
  
    void set_dtype(const int64_t &dtype);
    int64_t get_dtype() const;
    void set_right(const bool &right);
    bool get_right() const;
};

class OPS_API Muls : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Muls);
  Muls();

};

class OPS_API CrossEntropyLossGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CrossEntropyLossGrad);
  CrossEntropyLossGrad();

};

class OPS_API CumminExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CumminExt);
  CumminExt();

};

class OPS_API Randn : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Randn);
  Randn();

};

class OPS_API ReluGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReluGrad);
  ReluGrad();

};

class OPS_API InnerMoeTokenUnpermute : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerMoeTokenUnpermute);
  InnerMoeTokenUnpermute();

};

class OPS_API UniqueDim : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UniqueDim);
  UniqueDim();

};

class OPS_API RmsNormGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RmsNormGrad);
  RmsNormGrad();

};

class OPS_API Greater : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Greater);
  Greater();

};

class OPS_API NLLLoss : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NLLLoss);
  NLLLoss();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
    void set_ignore_index(const int64_t &ignore_index);
    int64_t get_ignore_index() const;
};

class OPS_API Cummin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cummin);
  Cummin();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API InplaceDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceDiv);
  InplaceDiv();

};

class OPS_API ReduceProd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceProd);
  ReduceProd();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API IsInf : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IsInf);
  IsInf();

};

class OPS_API ReduceMax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceMax);
  ReduceMax();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API SelectExtView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SelectExtView);
  SelectExtView();

};

class OPS_API InplaceCopy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceCopy);
  InplaceCopy();

};

class OPS_API TupleToTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TupleToTensor);
  TupleToTensor();

};

class OPS_API ArgMaxExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ArgMaxExt);
  ArgMaxExt();

};

class OPS_API TopkExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TopkExt);
  TopkExt();

};

class OPS_API NextAfter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NextAfter);
  NextAfter();

};

class OPS_API ToDevice : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ToDevice);
  ToDevice();

};

class OPS_API InsertGemV2InBackward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InsertGemV2InBackward);
  InsertGemV2InBackward();

};

class OPS_API InplaceFillDiagonal : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFillDiagonal);
  InplaceFillDiagonal();

};

class OPS_API GeluExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GeluExt);
  GeluExt();

};

class OPS_API BatchNormElemtGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormElemtGrad);
  BatchNormElemtGrad();

};

class OPS_API TensorScatterElements : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TensorScatterElements);
  TensorScatterElements();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_reduce(const int64_t &reduce);
    int64_t get_reduce() const;
};

class OPS_API SmoothL1LossGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SmoothL1LossGrad);
  SmoothL1LossGrad();
  
    void set_beta(const float &beta);
    float get_beta() const;
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API BatchNormElemt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormElemt);
  BatchNormElemt();

};

class OPS_API GluGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GluGrad);
  GluGrad();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API Lerp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Lerp);
  Lerp();

};

class OPS_API Nansum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Nansum);
  Nansum();

};

class OPS_API RandExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandExt);
  RandExt();

};

class OPS_API InplaceUniform : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceUniform);
  InplaceUniform();

};

class OPS_API InplaceDivMods : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceDivMods);
  InplaceDivMods();

};

class OPS_API Atan2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Atan2);
  Atan2();

};

class OPS_API ScalarMul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarMul);
  ScalarMul();

};

class OPS_API Tile : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Tile);
  Tile();

};

class OPS_API TopPRouter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TopPRouter);
  TopPRouter();

};

class OPS_API GatherNd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GatherNd);
  GatherNd();

};

class OPS_API MoeTokenUnpermuteGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeTokenUnpermuteGrad);
  MoeTokenUnpermuteGrad();

};

class OPS_API NPUGetFloatStatusV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NPUGetFloatStatusV2);
  NPUGetFloatStatusV2();

};

class OPS_API MatrixExp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatrixExp);
  MatrixExp();

};

class OPS_API LogitGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogitGrad);
  LogitGrad();
  
    void set_eps(const float &eps);
    float get_eps() const;
};

class OPS_API InplaceFloorDivides : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFloorDivides);
  InplaceFloorDivides();

};

class OPS_API Erf : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Erf);
  Erf();

};

class OPS_API MultinomialExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MultinomialExt);
  MultinomialExt();

};

class OPS_API DCT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DCT);
  DCT();

};

class OPS_API TraceExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TraceExt);
  TraceExt();

};

class OPS_API MoeTokenPermute : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeTokenPermute);
  MoeTokenPermute();

};

class OPS_API FillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FillScalar);
  FillScalar();

};

class OPS_API Scatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Scatter);
  Scatter();

};

class OPS_API LinalgVectorNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LinalgVectorNorm);
  LinalgVectorNorm();

};

class OPS_API DequantSwigluQuant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DequantSwigluQuant);
  DequantSwigluQuant();

};

class OPS_API HSigmoid : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HSigmoid);
  HSigmoid();

};

class OPS_API Geqrf : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Geqrf);
  Geqrf();

};

class OPS_API UpsampleBilinear2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleBilinear2D);
  UpsampleBilinear2D();

};

class OPS_API SmoothL1Loss : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SmoothL1Loss);
  SmoothL1Loss();
  
    void set_beta(const float &beta);
    float get_beta() const;
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API MeanExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MeanExt);
  MeanExt();

};

class OPS_API AcoshGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AcoshGrad);
  AcoshGrad();

};

class OPS_API AdaptiveAvgPool3DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveAvgPool3DExt);
  AdaptiveAvgPool3DExt();

};

class OPS_API BatchNormGatherStatsWithCounts : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGatherStatsWithCounts);
  BatchNormGatherStatsWithCounts();

};

class OPS_API Zeros : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Zeros);
  Zeros();

};

class OPS_API Kthvalue : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Kthvalue);
  Kthvalue();

};

class OPS_API HFFT2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HFFT2);
  HFFT2();

};

class OPS_API IsNegInf : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IsNegInf);
  IsNegInf();

};

class OPS_API UpsampleNearest1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest1D);
  UpsampleNearest1D();

};

class OPS_API Round : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Round);
  Round();

};

class OPS_API ImagView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ImagView);
  ImagView();

};

class OPS_API Softmax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Softmax);
  Softmax();
  
    void set_axis(const std::vector<int64_t> &axis);
    std::vector<int64_t> get_axis() const;
};

class OPS_API SliceExtView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SliceExtView);
  SliceExtView();

};

class OPS_API HardtanhGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HardtanhGrad);
  HardtanhGrad();

};

class OPS_API CholeskyGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CholeskyGrad);
  CholeskyGrad();

};

class OPS_API GridSampler2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GridSampler2D);
  GridSampler2D();
  
    void set_interpolation_mode(const int64_t &interpolation_mode);
    int64_t get_interpolation_mode() const;
    void set_padding_mode(const int64_t &padding_mode);
    int64_t get_padding_mode() const;
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
};

class OPS_API NormalFloatFloat : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NormalFloatFloat);
  NormalFloatFloat();

};

class OPS_API UpsampleBilinear2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleBilinear2DGrad);
  UpsampleBilinear2DGrad();

};

class OPS_API Col2ImGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Col2ImGrad);
  Col2ImGrad();

};

class OPS_API MaskedFillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaskedFillScalar);
  MaskedFillScalar();

};

class OPS_API PowScalarTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PowScalarTensor);
  PowScalarTensor();

};

class OPS_API InplaceDivMod : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceDivMod);
  InplaceDivMod();

};

class OPS_API Acosh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Acosh);
  Acosh();

};

class OPS_API FormatCast : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FormatCast);
  FormatCast();

};

class OPS_API ScalarUsub : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarUsub);
  ScalarUsub();

};

class OPS_API InplaceIndexFillTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceIndexFillTensor);
  InplaceIndexFillTensor();

};

class OPS_API BitwiseOrScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseOrScalar);
  BitwiseOrScalar();

};

class OPS_API GeLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GeLU);
  GeLU();

};

class OPS_API Gather : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Gather);
  Gather();
  
    void set_batch_dims(const int64_t &batch_dims);
    int64_t get_batch_dims() const;
};

class OPS_API MaxPoolGradWithMask : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxPoolGradWithMask);
  MaxPoolGradWithMask();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pads(const std::vector<int64_t> &pads);
    std::vector<int64_t> get_pads() const;
    void set_dilation(const std::vector<int64_t> &dilation);
    std::vector<int64_t> get_dilation() const;
    void set_ceil_mode(const bool &ceil_mode);
    bool get_ceil_mode() const;
    void set_argmax_type(const int64_t &argmax_type);
    int64_t get_argmax_type() const;
};

class OPS_API GreaterEqualScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GreaterEqualScalar);
  GreaterEqualScalar();

};

class OPS_API VarMean : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(VarMean);
  VarMean();

};

class OPS_API IsClose : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IsClose);
  IsClose();
  
    void set_rtol(const float &rtol);
    float get_rtol() const;
    void set_atol(const float &atol);
    float get_atol() const;
    void set_equal_nan(const bool &equal_nan);
    bool get_equal_nan() const;
};

class OPS_API InplaceMaskedScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMaskedScatter);
  InplaceMaskedScatter();

};

class OPS_API Argmin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Argmin);
  Argmin();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_output_type(const int64_t &output_type);
    int64_t get_output_type() const;
};

class OPS_API InplaceTanh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceTanh);
  InplaceTanh();

};

class OPS_API RandpermV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandpermV2);
  RandpermV2();
  
    void set_seed(const int64_t &seed);
    int64_t get_seed() const;
    void set_offset(const int64_t &offset);
    int64_t get_offset() const;
    void set_dtype(const int64_t &dtype);
    int64_t get_dtype() const;
};

class OPS_API GroupNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupNorm);
  GroupNorm();

};

class OPS_API ScalarToTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarToTensor);
  ScalarToTensor();

};

class OPS_API Tan : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Tan);
  Tan();

};

class OPS_API ReLU6Grad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReLU6Grad);
  ReLU6Grad();

};

class OPS_API MlaPreprocess : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MlaPreprocess);
  MlaPreprocess();

};

class OPS_API MultiScaleDeformableAttnGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MultiScaleDeformableAttnGrad);
  MultiScaleDeformableAttnGrad();

};

class OPS_API Svd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Svd);
  Svd();
  
    void set_full_matrices(const bool &full_matrices);
    bool get_full_matrices() const;
    void set_compute_uv(const bool &compute_uv);
    bool get_compute_uv() const;
};

class OPS_API TensorShape : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TensorShape);
  TensorShape();

};

class OPS_API IRFFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IRFFTN);
  IRFFTN();

};

class OPS_API InplaceIndexPut : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceIndexPut);
  InplaceIndexPut();

};

class OPS_API RemainderScalarTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RemainderScalarTensor);
  RemainderScalarTensor();

};

class OPS_API InplaceRemainderTensorTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceRemainderTensorTensor);
  InplaceRemainderTensorTensor();

};

class OPS_API ReflectionPad2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad2D);
  ReflectionPad2D();

};

class OPS_API BatchNormGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGrad);
  BatchNormGrad();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API RotaryPositionEmbedding : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RotaryPositionEmbedding);
  RotaryPositionEmbedding();

};

class OPS_API FloorDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FloorDiv);
  FloorDiv();

};

class OPS_API ApplyRotaryPosEmb : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyRotaryPosEmb);
  ApplyRotaryPosEmb();
  
    void set_cos_format(const int64_t &cos_format);
    int64_t get_cos_format() const;
};

class OPS_API ClampTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ClampTensor);
  ClampTensor();

};

class OPS_API EluGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EluGradExt);
  EluGradExt();

};

class OPS_API AssignAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AssignAdd);
  AssignAdd();

};

class OPS_API GeluGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GeluGradExt);
  GeluGradExt();

};

class OPS_API Conv1DPadding : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv1DPadding);
  Conv1DPadding();

};

class OPS_API Log1p : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Log1p);
  Log1p();

};

class OPS_API MaxPoolWithIndices : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxPoolWithIndices);
  MaxPoolWithIndices();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pads(const std::vector<int64_t> &pads);
    std::vector<int64_t> get_pads() const;
    void set_dilation(const std::vector<int64_t> &dilation);
    std::vector<int64_t> get_dilation() const;
    void set_ceil_mode(const bool &ceil_mode);
    bool get_ceil_mode() const;
    void set_argmax_type(const int64_t &argmax_type);
    int64_t get_argmax_type() const;
};

class OPS_API Unique2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Unique2);
  Unique2();

};

class OPS_API Rank : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Rank);
  Rank();

};

class OPS_API ScalarCast : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarCast);
  ScalarCast();

};

class OPS_API Atan2Ext : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Atan2Ext);
  Atan2Ext();

};

class OPS_API ReverseV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReverseV2);
  ReverseV2();
  
    void set_axis(const std::vector<int64_t> &axis);
    std::vector<int64_t> get_axis() const;
};

class OPS_API InplaceZero : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceZero);
  InplaceZero();

};

class OPS_API SpeedFusionAttention : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SpeedFusionAttention);
  SpeedFusionAttention();

};

class OPS_API TransposeExtView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TransposeExtView);
  TransposeExtView();

};

class OPS_API LerpScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LerpScalar);
  LerpScalar();

};

class OPS_API IFFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IFFTN);
  IFFTN();

};

class OPS_API SortExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SortExt);
  SortExt();

};

class OPS_API ReciprocalGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReciprocalGrad);
  ReciprocalGrad();

};

class OPS_API Conv2DPadding : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv2DPadding);
  Conv2DPadding();

};

class OPS_API SeluGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SeluGrad);
  SeluGrad();

};

class OPS_API Abs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Abs);
  Abs();

};

class OPS_API DropoutDoMaskExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DropoutDoMaskExt);
  DropoutDoMaskExt();

};

class OPS_API Betainc : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Betainc);
  Betainc();

};

class OPS_API SubScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SubScalar);
  SubScalar();

};

class OPS_API GridSampler2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GridSampler2DGrad);
  GridSampler2DGrad();
  
    void set_interpolation_mode(const int64_t &interpolation_mode);
    int64_t get_interpolation_mode() const;
    void set_padding_mode(const int64_t &padding_mode);
    int64_t get_padding_mode() const;
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_output_mask(const std::vector<int64_t> &output_mask);
    std::vector<int64_t> get_output_mask() const;
};

class OPS_API Sin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sin);
  Sin();

};

class OPS_API IRFFTDouble : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IRFFTDouble);
  IRFFTDouble();

};

class OPS_API UpsampleNearest3D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest3D);
  UpsampleNearest3D();

};

class OPS_API CrossEntropyLoss : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CrossEntropyLoss);
  CrossEntropyLoss();

};

class OPS_API InplaceNormal : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceNormal);
  InplaceNormal();

};

class OPS_API IDCT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IDCT);
  IDCT();

};

class OPS_API ScalarMin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarMin);
  ScalarMin();

};

class OPS_API LinSpaceExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LinSpaceExt);
  LinSpaceExt();

};

class OPS_API DumpGradient : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DumpGradient);
  DumpGradient();

};

class OPS_API BatchNormWithActivation : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormWithActivation);
  BatchNormWithActivation();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_momentum(const float &momentum);
    float get_momentum() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API LayerNormGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormGrad);
  LayerNormGrad();
  
    void set_begin_norm_axis(const int64_t &begin_norm_axis);
    int64_t get_begin_norm_axis() const;
    void set_begin_params_axis(const int64_t &begin_params_axis);
    int64_t get_begin_params_axis() const;
};

class OPS_API InplaceSubExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceSubExt);
  InplaceSubExt();

};

class OPS_API DivMods : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DivMods);
  DivMods();

};

class OPS_API AsinExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AsinExt);
  AsinExt();

};

class OPS_API ReduceMin : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceMin);
  ReduceMin();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API ACosGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ACosGrad);
  ACosGrad();

};

class OPS_API UpsampleLinear1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleLinear1D);
  UpsampleLinear1D();

};

class OPS_API ApplyCamePart3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ApplyCamePart3);
  ApplyCamePart3();

};

class OPS_API LogicalNot : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogicalNot);
  LogicalNot();

};

class OPS_API ArgMinExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ArgMinExt);
  ArgMinExt();

};

class OPS_API AdaptiveAvgPool2DGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveAvgPool2DGradExt);
  AdaptiveAvgPool2DGradExt();

};

class OPS_API FillTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FillTensor);
  FillTensor();

};

class OPS_API SilentCheckV3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SilentCheckV3);
  SilentCheckV3();

};

class OPS_API ACos : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ACos);
  ACos();

};

class OPS_API TransposeView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TransposeView);
  TransposeView();

};

class OPS_API ConvolutionStrGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ConvolutionStrGrad);
  ConvolutionStrGrad();

};

class OPS_API BitwiseOrTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseOrTensor);
  BitwiseOrTensor();

};

class OPS_API SigmoidGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SigmoidGrad);
  SigmoidGrad();

};

class OPS_API BoolNot : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BoolNot);
  BoolNot();

};

class OPS_API LinSpace : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LinSpace);
  LinSpace();

};

class OPS_API SplitWithSize : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SplitWithSize);
  SplitWithSize();

};

class OPS_API LogAddExp2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogAddExp2);
  LogAddExp2();

};

class OPS_API Convolution : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Convolution);
  Convolution();

};

class OPS_API CumSum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CumSum);
  CumSum();
  
    void set_exclusive(const bool &exclusive);
    bool get_exclusive() const;
    void set_reverse(const bool &reverse);
    bool get_reverse() const;
};

class OPS_API Min : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Min);
  Min();

};

class OPS_API BatchNormGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormGradExt);
  BatchNormGradExt();
  
    void set_training(const bool &training);
    bool get_training() const;
    void set_eps(const float &eps);
    float get_eps() const;
};

class OPS_API Range : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Range);
  Range();
  
    void set_maxlen(const int64_t &maxlen);
    int64_t get_maxlen() const;
};

class OPS_API FFTFreq : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTFreq);
  FFTFreq();

};

class OPS_API LogSigmoidGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSigmoidGrad);
  LogSigmoidGrad();

};

class OPS_API Identity : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Identity);
  Identity();

};

class OPS_API InplaceReLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceReLU);
  InplaceReLU();

};

class OPS_API Elu : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Elu);
  Elu();
  
    void set_alpha(const float &alpha);
    float get_alpha() const;
};

class OPS_API Mla : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Mla);
  Mla();

};

class OPS_API Var : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Var);
  Var();

};

class OPS_API ConvolutionStr : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ConvolutionStr);
  ConvolutionStr();

};

class OPS_API SeLUExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SeLUExt);
  SeLUExt();

};

class OPS_API ThresholdGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ThresholdGrad);
  ThresholdGrad();

};

class OPS_API Cos : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cos);
  Cos();

};

class OPS_API RotatedIou : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RotatedIou);
  RotatedIou();

};

class OPS_API NarrowView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NarrowView);
  NarrowView();

};

class OPS_API OneHot : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(OneHot);
  OneHot();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API ReduceSum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceSum);
  ReduceSum();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
    void set_skip_mode(const bool &skip_mode);
    bool get_skip_mode() const;
};

class OPS_API RandIntLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandIntLike);
  RandIntLike();

};

class OPS_API RealView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RealView);
  RealView();

};

class OPS_API EmptyLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EmptyLike);
  EmptyLike();

};

class OPS_API InplaceScatterValueReduce : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceScatterValueReduce);
  InplaceScatterValueReduce();

};

class OPS_API ProdExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ProdExt);
  ProdExt();

};

class OPS_API NewOnes : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NewOnes);
  NewOnes();

};

class OPS_API RightShift : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RightShift);
  RightShift();

};

class OPS_API Less : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Less);
  Less();

};

class OPS_API ArgMaxWithValue : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ArgMaxWithValue);
  ArgMaxWithValue();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API AddRmsNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddRmsNorm);
  AddRmsNorm();

};

class OPS_API GeLUGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GeLUGrad);
  GeLUGrad();

};

class OPS_API BatchNormReduceGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNormReduceGrad);
  BatchNormReduceGrad();

};

class OPS_API EqualExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EqualExt);
  EqualExt();

};

class OPS_API UpsampleNearest2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest2DGrad);
  UpsampleNearest2DGrad();

};

class OPS_API EluGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EluGrad);
  EluGrad();

};

class OPS_API Dense : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Dense);
  Dense();

};

class OPS_API ReflectionPad1DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReflectionPad1DGrad);
  ReflectionPad1DGrad();

};

class OPS_API NeScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NeScalar);
  NeScalar();

};

class OPS_API AvgPoolGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPoolGrad);
  AvgPoolGrad();
  
    void set_kernel_size(const std::vector<int64_t> &kernel_size);
    std::vector<int64_t> get_kernel_size() const;
    void set_strides(const std::vector<int64_t> &strides);
    std::vector<int64_t> get_strides() const;
    void set_pad_mode(const int64_t &pad_mode);
    int64_t get_pad_mode() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API Log10 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Log10);
  Log10();

};

class OPS_API PReLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PReLU);
  PReLU();

};

class OPS_API SoftShrink : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftShrink);
  SoftShrink();
  
    void set_lambd(const float &lambd);
    float get_lambd() const;
};

class OPS_API PowTensorScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PowTensorScalar);
  PowTensorScalar();

};

class OPS_API InplaceRandom : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceRandom);
  InplaceRandom();

};

class OPS_API InplaceElu : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceElu);
  InplaceElu();

};

class OPS_API ScalarGt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarGt);
  ScalarGt();

};

class OPS_API ScalarGe : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarGe);
  ScalarGe();

};

class OPS_API PagedAttentionMask : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PagedAttentionMask);
  PagedAttentionMask();
  
    void set_head_num(const int64_t &head_num);
    int64_t get_head_num() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_kv_head_num(const int64_t &kv_head_num);
    int64_t get_kv_head_num() const;
    void set_kv_cache_quant_mode(const int64_t &kv_cache_quant_mode);
    int64_t get_kv_cache_quant_mode() const;
};

class OPS_API AdaptiveAvgPool2DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveAvgPool2DExt);
  AdaptiveAvgPool2DExt();

};

class OPS_API ReplicationPad1DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad1DGrad);
  ReplicationPad1DGrad();

};

class OPS_API Cummax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Cummax);
  Cummax();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API ArgSort : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ArgSort);
  ArgSort();

};

class OPS_API ResizeBilinearV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeBilinearV2);
  ResizeBilinearV2();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API AdamWeightDecay : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdamWeightDecay);
  AdamWeightDecay();
  
    void set_use_locking(const bool &use_locking);
    bool get_use_locking() const;
};

class OPS_API CumsumExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CumsumExt);
  CumsumExt();

};

class OPS_API LpNormV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LpNormV2);
  LpNormV2();

};

class OPS_API AShardIdentity : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AShardIdentity);
  AShardIdentity();

};

class OPS_API ResizeNearestNeighborV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeNearestNeighborV2);
  ResizeNearestNeighborV2();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API NonZeroExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NonZeroExt);
  NonZeroExt();

};

class OPS_API AvgPool3DGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool3DGradExt);
  AvgPool3DGradExt();

};

class OPS_API InnerInplaceIndexPut : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerInplaceIndexPut);
  InnerInplaceIndexPut();

};

class OPS_API InplaceScatterSrc : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceScatterSrc);
  InplaceScatterSrc();

};

class OPS_API InplaceStopGradient : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceStopGradient);
  InplaceStopGradient();

};

class OPS_API Contiguous : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Contiguous);
  Contiguous();

};

class OPS_API ScalarDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarDiv);
  ScalarDiv();

};

class OPS_API FastGeLUGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FastGeLUGrad);
  FastGeLUGrad();

};

class OPS_API XLogYScalarSelf : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(XLogYScalarSelf);
  XLogYScalarSelf();

};

class OPS_API UnstackExtView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UnstackExtView);
  UnstackExtView();

};

class OPS_API Reshape : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Reshape);
  Reshape();

};

class OPS_API Gcd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Gcd);
  Gcd();

};

class OPS_API Repeat : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Repeat);
  Repeat();

};

class OPS_API LogicalOr : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogicalOr);
  LogicalOr();

};

class OPS_API MultiScaleDeformableAttn : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MultiScaleDeformableAttn);
  MultiScaleDeformableAttn();

};

class OPS_API UniformExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UniformExt);
  UniformExt();

};

class OPS_API ToOther : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ToOther);
  ToOther();

};

class OPS_API DiagonalView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DiagonalView);
  DiagonalView();
  
    void set_offset(const int64_t &offset);
    int64_t get_offset() const;
    void set_dim1(const int64_t &dim1);
    int64_t get_dim1() const;
    void set_dim2(const int64_t &dim2);
    int64_t get_dim2() const;
};

class OPS_API SoftmaxBackward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftmaxBackward);
  SoftmaxBackward();

};

class OPS_API FloorMod : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FloorMod);
  FloorMod();

};

class OPS_API InplaceFillTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceFillTensor);
  InplaceFillTensor();

};

class OPS_API SubExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SubExt);
  SubExt();

};

class OPS_API AllGatherMatmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AllGatherMatmul);
  AllGatherMatmul();

};

class OPS_API ZerosLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ZerosLike);
  ZerosLike();

};

class OPS_API ScatterAddExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScatterAddExt);
  ScatterAddExt();

};

class OPS_API IndexSelect : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IndexSelect);
  IndexSelect();

};

class OPS_API NewZeros : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NewZeros);
  NewZeros();

};

class OPS_API MinimumGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MinimumGrad);
  MinimumGrad();
  
    void set_grad_x(const bool &grad_x);
    bool get_grad_x() const;
    void set_grad_y(const bool &grad_y);
    bool get_grad_y() const;
};

class OPS_API MaxUnpool2DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxUnpool2DExt);
  MaxUnpool2DExt();

};

class OPS_API ReLU6 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReLU6);
  ReLU6();

};

class OPS_API Complex : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Complex);
  Complex();

};

class OPS_API TriangularSolve : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TriangularSolve);
  TriangularSolve();

};

class OPS_API LogSoftmax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSoftmax);
  LogSoftmax();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API AddcdivExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddcdivExt);
  AddcdivExt();

};

class OPS_API LogicalAnd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogicalAnd);
  LogicalAnd();

};

class OPS_API Erfc : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Erfc);
  Erfc();

};

class OPS_API HSwish : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HSwish);
  HSwish();

};

class OPS_API Diag : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Diag);
  Diag();

};

class OPS_API RandnLike : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RandnLike);
  RandnLike();

};

class OPS_API MatMulExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatMulExt);
  MatMulExt();

};

class OPS_API Narrow : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Narrow);
  Narrow();

};

class OPS_API ArgMinWithValue : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ArgMinWithValue);
  ArgMinWithValue();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API StridedSlice : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(StridedSlice);
  StridedSlice();
  
    void set_begin_mask(const int64_t &begin_mask);
    int64_t get_begin_mask() const;
    void set_end_mask(const int64_t &end_mask);
    int64_t get_end_mask() const;
    void set_ellipsis_mask(const int64_t &ellipsis_mask);
    int64_t get_ellipsis_mask() const;
    void set_new_axis_mask(const int64_t &new_axis_mask);
    int64_t get_new_axis_mask() const;
    void set_shrink_axis_mask(const int64_t &shrink_axis_mask);
    int64_t get_shrink_axis_mask() const;
};

class OPS_API AsinGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AsinGrad);
  AsinGrad();

};

class OPS_API Conv3DPadding : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Conv3DPadding);
  Conv3DPadding();

};

class OPS_API AvgPool3DExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool3DExt);
  AvgPool3DExt();

};

class OPS_API HFFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HFFT);
  HFFT();

};

class OPS_API ScalarAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarAdd);
  ScalarAdd();

};

class OPS_API InplaceExp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceExp);
  InplaceExp();

};

class OPS_API TupleToList : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TupleToList);
  TupleToList();

};

class OPS_API Shape : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Shape);
  Shape();

};

class OPS_API Rsqrt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Rsqrt);
  Rsqrt();

};

class OPS_API InplaceRemainderTensorScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceRemainderTensorScalar);
  InplaceRemainderTensorScalar();

};

class OPS_API ResizeNearestNeighborV2Grad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeNearestNeighborV2Grad);
  ResizeNearestNeighborV2Grad();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API FastGeLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FastGeLU);
  FastGeLU();

};

class OPS_API LogSigmoid : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LogSigmoid);
  LogSigmoid();

};

class OPS_API UpsampleNearest2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest2D);
  UpsampleNearest2D();

};

class OPS_API IsFinite : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IsFinite);
  IsFinite();

};

class OPS_API BitwiseAndScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseAndScalar);
  BitwiseAndScalar();

};

class OPS_API ReplicationPad2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad2D);
  ReplicationPad2D();

};

class OPS_API LstsqV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LstsqV2);
  LstsqV2();

};

class OPS_API FmodTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FmodTensor);
  FmodTensor();

};

class OPS_API MaxDim : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaxDim);
  MaxDim();

};

class OPS_API RmsNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RmsNorm);
  RmsNorm();
  
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
};

class OPS_API Outer : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Outer);
  Outer();

};

class OPS_API FFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFT);
  FFT();

};

class OPS_API PReLUGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PReLUGrad);
  PReLUGrad();

};

class OPS_API NPUClearFloatStatusV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NPUClearFloatStatusV2);
  NPUClearFloatStatusV2();

};

class OPS_API InplacePut : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplacePut);
  InplacePut();

};

class OPS_API FlashAttentionScoreGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FlashAttentionScoreGrad);
  FlashAttentionScoreGrad();
  
    void set_head_num(const int64_t &head_num);
    int64_t get_head_num() const;
    void set_keep_prob(const float &keep_prob);
    float get_keep_prob() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_pre_tokens(const int64_t &pre_tokens);
    int64_t get_pre_tokens() const;
    void set_next_tokens(const int64_t &next_tokens);
    int64_t get_next_tokens() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
    void set_input_layout(const int64_t &input_layout);
    int64_t get_input_layout() const;
    void set_sparse_mode(const int64_t &sparse_mode);
    int64_t get_sparse_mode() const;
};

class OPS_API Sqrt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sqrt);
  Sqrt();

};

class OPS_API AvgPool2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AvgPool2D);
  AvgPool2D();

};

class OPS_API UpsampleNearest1DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleNearest1DGrad);
  UpsampleNearest1DGrad();

};

class OPS_API InplaceSigmoid : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceSigmoid);
  InplaceSigmoid();

};

class OPS_API NLLLoss2dGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NLLLoss2dGrad);
  NLLLoss2dGrad();

};

class OPS_API RepeatInterleaveGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RepeatInterleaveGrad);
  RepeatInterleaveGrad();

};

class OPS_API ReplicationPad2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReplicationPad2DGrad);
  ReplicationPad2DGrad();

};

class OPS_API Divs : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Divs);
  Divs();

};

class OPS_API ResizeLinear1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeLinear1D);
  ResizeLinear1D();
  
    void set_coordinate_transformation_mode(const int64_t &coordinate_transformation_mode);
    int64_t get_coordinate_transformation_mode() const;
};

class OPS_API IndexFillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IndexFillScalar);
  IndexFillScalar();

};

class OPS_API Index : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Index);
  Index();

};

class OPS_API TopKRouter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TopKRouter);
  TopKRouter();

};

class OPS_API GLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GLU);
  GLU();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API SliceExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SliceExt);
  SliceExt();

};

class OPS_API AbsGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AbsGrad);
  AbsGrad();

};

class OPS_API SwigluGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SwigluGrad);
  SwigluGrad();

};

class OPS_API ExpandDimsView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ExpandDimsView);
  ExpandDimsView();

};

class OPS_API NormalTensorFloat : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NormalTensorFloat);
  NormalTensorFloat();

};

class OPS_API FusedAddTopKDiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FusedAddTopKDiv);
  FusedAddTopKDiv();

};

class OPS_API Xlogy : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Xlogy);
  Xlogy();

};

class OPS_API UpsampleBicubic2DGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UpsampleBicubic2DGrad);
  UpsampleBicubic2DGrad();

};

class OPS_API OneHotExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(OneHotExt);
  OneHotExt();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
};

class OPS_API SiLU : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SiLU);
  SiLU();

};

class OPS_API Ones : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Ones);
  Ones();

};

class OPS_API MatMul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatMul);
  MatMul();
  
    void set_transpose_a(const bool &transpose_a);
    bool get_transpose_a() const;
    void set_transpose_b(const bool &transpose_b);
    bool get_transpose_b() const;
};

class OPS_API AdaptiveMaxPool1D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AdaptiveMaxPool1D);
  AdaptiveMaxPool1D();

};

class OPS_API InnerIndex : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerIndex);
  InnerIndex();

};

class OPS_API MoeDistributeDispatch : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeDistributeDispatch);
  MoeDistributeDispatch();

};

class OPS_API SoftShrinkGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftShrinkGrad);
  SoftShrinkGrad();
  
    void set_lambd(const float &lambd);
    float get_lambd() const;
};

class OPS_API SoftplusGradExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SoftplusGradExt);
  SoftplusGradExt();

};

class OPS_API InplaceMaskedFillTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceMaskedFillTensor);
  InplaceMaskedFillTensor();

};

class OPS_API NotEqual : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(NotEqual);
  NotEqual();

};

class OPS_API Frac : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Frac);
  Frac();

};

class OPS_API SplitTensorView : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SplitTensorView);
  SplitTensorView();

};

class OPS_API KvScaleCache : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(KvScaleCache);
  KvScaleCache();

};

class OPS_API LayerNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNorm);
  LayerNorm();
  
    void set_begin_norm_axis(const int64_t &begin_norm_axis);
    int64_t get_begin_norm_axis() const;
    void set_begin_params_axis(const int64_t &begin_params_axis);
    int64_t get_begin_params_axis() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
};

class OPS_API AssignSub : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AssignSub);
  AssignSub();

};

class OPS_API ReshapeAndCache : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReshapeAndCache);
  ReshapeAndCache();

};

class OPS_API SpeedFusionAttentionGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SpeedFusionAttentionGrad);
  SpeedFusionAttentionGrad();

};

class OPS_API MatmulReduceScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulReduceScatter);
  MatmulReduceScatter();

};

class OPS_API ResizeNearestNeighborGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ResizeNearestNeighborGrad);
  ResizeNearestNeighborGrad();
  
    void set_align_corners(const bool &align_corners);
    bool get_align_corners() const;
    void set_half_pixel_centers(const bool &half_pixel_centers);
    bool get_half_pixel_centers() const;
};

class OPS_API SilentCheckV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SilentCheckV2);
  SilentCheckV2();

};

class OPS_API ClampScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ClampScalar);
  ClampScalar();

};

class OPS_API Exp : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Exp);
  Exp();

};

class OPS_API MatrixDeterminant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatrixDeterminant);
  MatrixDeterminant();

};

class OPS_API Split : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Split);
  Split();
  
    void set_axis(const int64_t &axis);
    int64_t get_axis() const;
    void set_output_num(const int64_t &output_num);
    int64_t get_output_num() const;
};

class OPS_API InplaceIndexFillScalar : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceIndexFillScalar);
  InplaceIndexFillScalar();

};

class OPS_API IndexFillTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IndexFillTensor);
  IndexFillTensor();

};

class OPS_API Embedding : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Embedding);
  Embedding();

};

class OPS_API BatchNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchNorm);
  BatchNorm();
  
    void set_is_training(const bool &is_training);
    bool get_is_training() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
    void set_momentum(const float &momentum);
    float get_momentum() const;
    void set_data_format(const int64_t &data_format);
    int64_t get_data_format() const;
};

class OPS_API LeakyReLUExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LeakyReLUExt);
  LeakyReLUExt();

};

class OPS_API Maximum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Maximum);
  Maximum();

};

class OPS_API ReduceAny : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceAny);
  ReduceAny();
  
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API Floor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Floor);
  Floor();

};

class OPS_API FFTShift : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTShift);
  FFTShift();

};

class OPS_API AddN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddN);
  AddN();

};

class OPS_API Clone : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Clone);
  Clone();

};

class OPS_API Swiglu : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Swiglu);
  Swiglu();

};

class OPS_API HFFTN : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(HFFTN);
  HFFTN();

};

class OPS_API BernoulliExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BernoulliExt);
  BernoulliExt();

};

class OPS_API BitwiseAndTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BitwiseAndTensor);
  BitwiseAndTensor();

};

class OPS_API Equal : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Equal);
  Equal();

};

class OPS_API UnsortedSegmentSum : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(UnsortedSegmentSum);
  UnsortedSegmentSum();

};

class OPS_API MaximumGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaximumGrad);
  MaximumGrad();
  
    void set_grad_x(const bool &grad_x);
    bool get_grad_x() const;
    void set_grad_y(const bool &grad_y);
    bool get_grad_y() const;
};

class OPS_API DivMod : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DivMod);
  DivMod();

};

class OPS_API Neg : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Neg);
  Neg();

};

class OPS_API Sinh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Sinh);
  Sinh();

};

class OPS_API InplaceScatterAdd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceScatterAdd);
  InplaceScatterAdd();

};

class OPS_API ConstantPadND : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ConstantPadND);
  ConstantPadND();

};

class OPS_API Pow : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Pow);
  Pow();

};

class OPS_API IndexAddExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IndexAddExt);
  IndexAddExt();

};

class OPS_API LayerNormGradV3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormGradV3);
  LayerNormGradV3();
  
    void set_begin_norm_axis(const int64_t &begin_norm_axis);
    int64_t get_begin_norm_axis() const;
    void set_begin_params_axis(const int64_t &begin_params_axis);
    int64_t get_begin_params_axis() const;
};

class OPS_API InplaceAddExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceAddExt);
  InplaceAddExt();

};

class OPS_API SumExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SumExt);
  SumExt();

};

class OPS_API Addcdiv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Addcdiv);
  Addcdiv();

};

class OPS_API Flatten : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Flatten);
  Flatten();

};

class OPS_API L1LossExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(L1LossExt);
  L1LossExt();

};

class OPS_API InplaceThreshold : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceThreshold);
  InplaceThreshold();

};

class OPS_API ScalarMod : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarMod);
  ScalarMod();

};

class OPS_API PagedAttention : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PagedAttention);
  PagedAttention();
  
    void set_head_num(const int64_t &head_num);
    int64_t get_head_num() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_kv_head_num(const int64_t &kv_head_num);
    int64_t get_kv_head_num() const;
    void set_kv_cache_quant_mode(const int64_t &kv_cache_quant_mode);
    int64_t get_kv_cache_quant_mode() const;
    void set_mask_mode(const int64_t &mask_mode);
    int64_t get_mask_mode() const;
    void set_mla_v_dim(const int64_t &mla_v_dim);
    int64_t get_mla_v_dim() const;
};

class OPS_API AcoshExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AcoshExt);
  AcoshExt();

};

class OPS_API Addmm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Addmm);
  Addmm();

};

class OPS_API SqrtGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SqrtGrad);
  SqrtGrad();

};

class OPS_API Hardtanh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Hardtanh);
  Hardtanh();

};

class OPS_API MaskedSelect : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MaskedSelect);
  MaskedSelect();

};

class OPS_API FFTOrtho : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FFTOrtho);
  FFTOrtho();

};

class OPS_API Asinh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Asinh);
  Asinh();

};

class OPS_API LayerNormV3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(LayerNormV3);
  LayerNormV3();
  
    void set_begin_norm_axis(const int64_t &begin_norm_axis);
    int64_t get_begin_norm_axis() const;
    void set_begin_params_axis(const int64_t &begin_params_axis);
    int64_t get_begin_params_axis() const;
    void set_epsilon(const float &epsilon);
    float get_epsilon() const;
};

class OPS_API ReduceStd : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ReduceStd);
  ReduceStd();
  
    void set_axis(const std::vector<int64_t> &axis);
    std::vector<int64_t> get_axis() const;
    void set_unbiased(const bool &unbiased);
    bool get_unbiased() const;
    void set_keep_dims(const bool &keep_dims);
    bool get_keep_dims() const;
};

class OPS_API BinaryCrossEntropyGrad : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BinaryCrossEntropyGrad);
  BinaryCrossEntropyGrad();
  
    void set_reduction(const int64_t &reduction);
    int64_t get_reduction() const;
};

class OPS_API RFFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RFFT);
  RFFT();

};

class OPS_API Ceil : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Ceil);
  Ceil();

};

class OPS_API BatchMatMul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(BatchMatMul);
  BatchMatMul();
  
    void set_transpose_a(const bool &transpose_a);
    bool get_transpose_a() const;
    void set_transpose_b(const bool &transpose_b);
    bool get_transpose_b() const;
};

class OPS_API CountNonZero : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(CountNonZero);
  CountNonZero();

};

class OPS_API IHFFT : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(IHFFT);
  IHFFT();

};

class OPS_API ScalarPow : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarPow);
  ScalarPow();

};

class OPS_API Addmv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Addmv);
  Addmv();

};

class OPS_API InplaceHardtanh : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceHardtanh);
  InplaceHardtanh();

};

class OPS_API Atan : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Atan);
  Atan();

};

class OPS_API ScalarMax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(ScalarMax);
  ScalarMax();

};

class OPS_API InplaceBernoulliTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceBernoulliTensor);
  InplaceBernoulliTensor();

};

class OPS_API QuantMatmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantMatmul);
  QuantMatmul();

};

class OPS_API MatmulBiasSplitOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulBiasSplitOut2);
  MatmulBiasSplitOut2();

};

class OPS_API MoeInitRouting : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeInitRouting);
  MoeInitRouting();

};

class OPS_API MatmulSplitOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulSplitOut2);
  MatmulSplitOut2();

};

class OPS_API WeightQuantBatchMatmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(WeightQuantBatchMatmul);
  WeightQuantBatchMatmul();
  
    void set_transpose_x(const bool &transpose_x);
    bool get_transpose_x() const;
    void set_transpose_weight(const bool &transpose_weight);
    bool get_transpose_weight() const;
    void set_antiquant_group_size(const int64_t &antiquant_group_size);
    int64_t get_antiquant_group_size() const;
};

class OPS_API RmsNormQuant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(RmsNormQuant);
  RmsNormQuant();

};

class OPS_API MatmulSplitSiluFastgeluAddMulOut1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulSplitSiluFastgeluAddMulOut1);
  MatmulSplitSiluFastgeluAddMulOut1();

};

class OPS_API QuantV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantV2);
  QuantV2();

};

class OPS_API GroupedMatmulV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupedMatmulV2);
  GroupedMatmulV2();

};

class OPS_API MatmulBiasSplitOut3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulBiasSplitOut3);
  MatmulBiasSplitOut3();

};

class OPS_API MatmulSplitSiluMulOut1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulSplitSiluMulOut1);
  MatmulSplitSiluMulOut1();

};

class OPS_API MoeGatingTopKSoftmax : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeGatingTopKSoftmax);
  MoeGatingTopKSoftmax();

};

class OPS_API KVCacheScatterUpdate : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(KVCacheScatterUpdate);
  KVCacheScatterUpdate();

};

class OPS_API MatmulSplitSiluOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulSplitSiluOut2);
  MatmulSplitSiluOut2();

};

class OPS_API QuantbatchmatmulSplitOut3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantbatchmatmulSplitOut3);
  QuantbatchmatmulSplitOut3();

};

class OPS_API QMatmulSplitSiluFastgeluAddMulOut1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QMatmulSplitSiluFastgeluAddMulOut1);
  QMatmulSplitSiluFastgeluAddMulOut1();

};

class OPS_API GroupedMatmulV4 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupedMatmulV4);
  GroupedMatmulV4();

};

class OPS_API QuantbatchmatmulSplitSiluOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantbatchmatmulSplitSiluOut2);
  QuantbatchmatmulSplitSiluOut2();

};

class OPS_API MatmulSplitOut3 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulSplitOut3);
  MatmulSplitOut3();

};

class OPS_API MoeFinalizeRouting : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeFinalizeRouting);
  MoeFinalizeRouting();

};

class OPS_API QuantbatchmatmulSplitOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantbatchmatmulSplitOut2);
  QuantbatchmatmulSplitOut2();

};

class OPS_API SwiGLUDynamicQuant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(SwiGLUDynamicQuant);
  SwiGLUDynamicQuant();

};

class OPS_API AddRmsNormDynamicQuant : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddRmsNormDynamicQuant);
  AddRmsNormDynamicQuant();

};

class OPS_API FusedMatmulElemBinary : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FusedMatmulElemBinary);
  FusedMatmulElemBinary();

};

class OPS_API FusedMatmulElemUnary : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FusedMatmulElemUnary);
  FusedMatmulElemUnary();

};

class OPS_API GroupedMatmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GroupedMatmul);
  GroupedMatmul();
  
    void set_split_item(const int64_t &split_item);
    int64_t get_split_item() const;
    void set_group_type(const int64_t &group_type);
    int64_t get_group_type() const;
    void set_transpose_a(const bool &transpose_a);
    bool get_transpose_a() const;
    void set_transpose_b(const bool &transpose_b);
    bool get_transpose_b() const;
};

class OPS_API FusedInferAttentionScore : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FusedInferAttentionScore);
  FusedInferAttentionScore();
  
    void set_num_heads(const int64_t &num_heads);
    int64_t get_num_heads() const;
    void set_scale_value(const float &scale_value);
    float get_scale_value() const;
    void set_pre_tokens(const int64_t &pre_tokens);
    int64_t get_pre_tokens() const;
    void set_next_tokens(const int64_t &next_tokens);
    int64_t get_next_tokens() const;
    void set_input_layout(const int64_t &input_layout);
    int64_t get_input_layout() const;
    void set_num_key_value_heads(const int64_t &num_key_value_heads);
    int64_t get_num_key_value_heads() const;
    void set_sparse_mode(const int64_t &sparse_mode);
    int64_t get_sparse_mode() const;
    void set_inner_precise(const int64_t &inner_precise);
    int64_t get_inner_precise() const;
    void set_block_size(const int64_t &block_size);
    int64_t get_block_size() const;
    void set_antiquant_mode(const int64_t &antiquant_mode);
    int64_t get_antiquant_mode() const;
    void set_softmax_lse_flag(const bool &softmax_lse_flag);
    bool get_softmax_lse_flag() const;
    void set_key_antiquant_mode(const int64_t &key_antiquant_mode);
    int64_t get_key_antiquant_mode() const;
    void set_value_antiquant_mode(const int64_t &value_antiquant_mode);
    int64_t get_value_antiquant_mode() const;
};

class OPS_API TransposeBatchMatmulTranspose : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TransposeBatchMatmulTranspose);
  TransposeBatchMatmulTranspose();

};

class OPS_API MoeInitRoutingV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeInitRoutingV2);
  MoeInitRoutingV2();

};

class OPS_API DynamicQuantExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DynamicQuantExt);
  DynamicQuantExt();

};

class OPS_API QuantBatchMatmul : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantBatchMatmul);
  QuantBatchMatmul();
  
    void set_transpose_x1(const bool &transpose_x1);
    bool get_transpose_x1() const;
    void set_transpose_x2(const bool &transpose_x2);
    bool get_transpose_x2() const;
    void set_dtype(const int64_t &dtype);
    int64_t get_dtype() const;
};

class OPS_API QuantLinearSparse : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QuantLinearSparse);
  QuantLinearSparse();

};

class OPS_API QMatmulSplitSiluMulOut1 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(QMatmulSplitSiluMulOut1);
  QMatmulSplitSiluMulOut1();

};

class OPS_API DynamicNTK : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DynamicNTK);
  DynamicNTK();

};

class OPS_API MatmulAllReduceAddRmsNorm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulAllReduceAddRmsNorm);
  MatmulAllReduceAddRmsNorm();

};

class OPS_API AddRmsNormQuantV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AddRmsNormQuantV2);
  AddRmsNormQuantV2();

};

class OPS_API MoeInitRoutingQuantV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeInitRoutingQuantV2);
  MoeInitRoutingQuantV2();

};

class OPS_API MoeComputeExpertTokens : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeComputeExpertTokens);
  MoeComputeExpertTokens();

};

class OPS_API TransData : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(TransData);
  TransData();

};

class OPS_API MatmulBiasSplitSiluOut2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MatmulBiasSplitSiluOut2);
  MatmulBiasSplitSiluOut2();

};

class OPS_API DistCommScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommScatter);
  DistCommScatter();

};

class OPS_API DistCommAllGather : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllGather);
  DistCommAllGather();

};

class OPS_API InnerCommAllToAllV : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommAllToAllV);
  InnerCommAllToAllV();

};

class OPS_API InnerCommIsend : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommIsend);
  InnerCommIsend();

};

class OPS_API DistCommGatherIntoTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommGatherIntoTensor);
  DistCommGatherIntoTensor();

};

class OPS_API InnerCommIrecv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommIrecv);
  InnerCommIrecv();

};

class OPS_API DistCommBroadcast : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommBroadcast);
  DistCommBroadcast();

};

class OPS_API DistCommAllGatherIntoTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllGatherIntoTensor);
  DistCommAllGatherIntoTensor();

};

class OPS_API DistCommGather : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommGather);
  DistCommGather();

};

class OPS_API DistCommIsend : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommIsend);
  DistCommIsend();

};

class OPS_API InnerCommAllGather : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommAllGather);
  InnerCommAllGather();

};

class OPS_API DistCommIrecv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommIrecv);
  DistCommIrecv();

};

class OPS_API DistCommReduceScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommReduceScatter);
  DistCommReduceScatter();

};

class OPS_API DistCommBarrier : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommBarrier);
  DistCommBarrier();

};

class OPS_API DistCommReduce : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommReduce);
  DistCommReduce();

};

class OPS_API DistCommScatterTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommScatterTensor);
  DistCommScatterTensor();

};

class OPS_API DistCommAllGatherIntoTensorUneven : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllGatherIntoTensorUneven);
  DistCommAllGatherIntoTensorUneven();

};

class OPS_API DistCommAllToAllV : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllToAllV);
  DistCommAllToAllV();

};

class OPS_API DistCommAllToAllVSingle : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllToAllVSingle);
  DistCommAllToAllVSingle();

};

class OPS_API DistCommReduceScatterTensorUneven : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommReduceScatterTensorUneven);
  DistCommReduceScatterTensorUneven();

};

class OPS_API DistCommAllReduce : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllReduce);
  DistCommAllReduce();

};

class OPS_API DistCommAllToAllVC : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommAllToAllVC);
  DistCommAllToAllVC();

};

class OPS_API DistCommReduceScatterTensor : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommReduceScatterTensor);
  DistCommReduceScatterTensor();

};

class OPS_API InnerCommReduceScatter : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommReduceScatter);
  InnerCommReduceScatter();

};

class OPS_API DistCommBatchIsendIrecv : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(DistCommBatchIsendIrecv);
  DistCommBatchIsendIrecv();

};

class OPS_API InnerCommAllReduce : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InnerCommAllReduce);
  InnerCommAllReduce();

};

class OPS_API GmmBackward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GmmBackward);
  GmmBackward();

};

class OPS_API GmmBackwardFusion : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GmmBackwardFusion);
  GmmBackwardFusion();

};

class OPS_API GmmV2 : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GmmV2);
  GmmV2();

};

class OPS_API InplaceExponential : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(InplaceExponential);
  InplaceExponential();

};

class OPS_API GmmV2Backward : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GmmV2Backward);
  GmmV2Backward();

};

class OPS_API AnyExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(AnyExt);
  AnyExt();

};

class OPS_API GmmV2BackwardFusion : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(GmmV2BackwardFusion);
  GmmV2BackwardFusion();

};

class OPS_API FuncMaxPool2D : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FuncMaxPool2D);
  FuncMaxPool2D();

};

class OPS_API FuncDropoutExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(FuncDropoutExt);
  FuncDropoutExt();

};

class OPS_API PixelShuffle : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(PixelShuffle);
  PixelShuffle();

};

class OPS_API Dropout2dExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Dropout2dExt);
  Dropout2dExt();

};

class OPS_API EinsumExt : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(EinsumExt);
  EinsumExt();

};

class OPS_API Any : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Any);
  Any();

};

class OPS_API Gmm : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(Gmm);
  Gmm();

};

class OPS_API MoeTokenUnpermute : public BaseOperator {
 public:
  MIND_API_BASE_MEMBER(MoeTokenUnpermute);
  MoeTokenUnpermute();

};

}  // namespace mindspore::ops
#endif  // MINDSPORE_CORE_OPS_GEN_LITE_OPS_H_
