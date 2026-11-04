// Local-only JNI bridge to the official MindSpore Lite CPU static library.
// Link the complete operator registry into a real 16 KB aligned shared object.
#include <jni.h>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
#include "include/api/model.h"
#include "include/api/context.h"

namespace {
constexpr size_t kTokens = 256;
struct Engine {
  mindspore::Model model;
  std::vector<mindspore::MSTensor> inputs;
  std::mutex mutex;
};
std::mutex registry_mutex;
std::unordered_map<jlong, std::shared_ptr<Engine>> registry;
jlong next_handle = 1;

void Throw(JNIEnv *env, const char *type, const std::string &message) {
  if (env->ExceptionCheck()) return;
  jclass error = env->FindClass(type);
  if (error) env->ThrowNew(error, message.c_str());
}

std::shared_ptr<Engine> Lookup(jlong handle) {
  std::lock_guard<std::mutex> lock(registry_mutex);
  auto found = registry.find(handle);
  if (found == registry.end()) throw std::invalid_argument("WiseMessage native model is closed or unavailable");
  return found->second;
}

void CheckInput(JNIEnv *env, jintArray array) {
  if (!array || env->GetArrayLength(array) != static_cast<jsize>(kTokens))
    throw std::invalid_argument("WiseMessage requires exactly 256 int32 tokens per input");
}
}  // namespace

extern "C" JNIEXPORT jlong JNICALL
Java_hk_wisemessage_app_ml_NativeMessageEngine_create(JNIEnv *env, jclass, jobject buffer, jint threads) {
  try {
    if (!buffer || threads < 1 || threads > 8) throw std::invalid_argument("Invalid model buffer or CPU thread count");
    auto address = env->GetDirectBufferAddress(buffer);
    auto capacity = env->GetDirectBufferCapacity(buffer);
    if (!address || capacity < 1024) throw std::invalid_argument("Model must be a direct nonempty ByteBuffer");
    auto context = std::make_shared<mindspore::Context>();
    context->SetThreadNum(threads);
    context->SetThreadAffinity(0);
    auto cpu = std::make_shared<mindspore::CPUDeviceInfo>();
    cpu->SetEnableFP16(false);
    context->MutableDeviceInfo().push_back(cpu);
    auto engine = std::make_shared<Engine>();
    auto status = engine->model.Build(address, static_cast<size_t>(capacity), mindspore::ModelType::kMindIR_Lite, context);
    if (status != mindspore::kSuccess) throw std::runtime_error("MindSpore Lite failed to build the bundled model: " + status.ToString());
    engine->inputs = engine->model.GetInputs();
    if (engine->inputs.size() != 3) throw std::runtime_error("Expected three model inputs");
    for (const auto &input : engine->inputs) {
      if (input.Shape() != std::vector<int64_t>({1, 256}) ||
          input.DataType() != mindspore::DataType::kNumberTypeInt32 || input.DataSize() != kTokens * sizeof(jint))
        throw std::runtime_error("Unexpected input tensor shape or type: " + input.Name());
      if (input.Name() != "input_ids" && input.Name() != "attention_mask" && input.Name() != "token_type_ids")
        throw std::runtime_error("Unexpected model input name: " + input.Name());
    }
    std::lock_guard<std::mutex> lock(registry_mutex);
    const jlong handle = next_handle++;
    registry.emplace(handle, engine);
    return handle;
  } catch (const std::invalid_argument &error) {
    Throw(env, "java/lang/IllegalArgumentException", error.what());
  } catch (const std::exception &error) {
    Throw(env, "java/io/IOException", error.what());
  } catch (...) {
    Throw(env, "java/io/IOException", "Unexpected error while loading the local MindSpore model");
  }
  return 0;
}

extern "C" JNIEXPORT jfloatArray JNICALL
Java_hk_wisemessage_app_ml_NativeMessageEngine_predict(JNIEnv *env, jclass, jlong handle,
                                                      jintArray ids, jintArray mask, jintArray types) {
  try {
    CheckInput(env, ids);
    CheckInput(env, mask);
    CheckInput(env, types);
    auto engine = Lookup(handle);
    std::lock_guard<std::mutex> lock(engine->mutex);
    for (auto &input : engine->inputs) {
      jintArray values = input.Name() == "input_ids" ? ids : input.Name() == "attention_mask" ? mask : types;
      auto data = reinterpret_cast<jint *>(input.MutableData());
      if (!data) throw std::runtime_error("MindSpore Lite input allocation failed");
      env->GetIntArrayRegion(values, 0, kTokens, data);
      if (env->ExceptionCheck()) return nullptr;
    }
    std::vector<mindspore::MSTensor> outputs;
    auto status = engine->model.Predict(engine->inputs, &outputs);
    if (status != mindspore::kSuccess) throw std::runtime_error("MindSpore Lite inference failed: " + status.ToString());
    if (outputs.size() != 1 || outputs[0].DataType() != mindspore::DataType::kNumberTypeFloat32 || outputs[0].DataSize() != 3 * sizeof(float))
      throw std::runtime_error("Unexpected classifier output shape or dtype");
    auto values = reinterpret_cast<const float *>(outputs[0].Data().get());
    if (!values || !std::isfinite(values[0]) || !std::isfinite(values[1]) || !std::isfinite(values[2]))
      throw std::runtime_error("Classifier produced invalid scores");
    jfloatArray result = env->NewFloatArray(3);
    if (result) env->SetFloatArrayRegion(result, 0, 3, values);
    return result;
  } catch (const std::invalid_argument &error) {
    Throw(env, "java/lang/IllegalArgumentException", error.what());
  } catch (const std::exception &error) {
    Throw(env, "java/io/IOException", error.what());
  } catch (...) {
    Throw(env, "java/io/IOException", "Unexpected error during local MindSpore inference");
  }
  return nullptr;
}

extern "C" JNIEXPORT void JNICALL
Java_hk_wisemessage_app_ml_NativeMessageEngine_destroy(JNIEnv *, jclass, jlong handle) {
  std::lock_guard<std::mutex> lock(registry_mutex);
  registry.erase(handle);
}
