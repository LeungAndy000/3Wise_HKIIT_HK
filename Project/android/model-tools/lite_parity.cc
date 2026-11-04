#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include "include/api/model.h"
#include "include/api/context.h"

int main(int argc, char **argv) {
  if (argc != 4) { std::cerr << "model.ms export_dir samples\n"; return 2; }
  auto context = std::make_shared<mindspore::Context>();
  context->SetThreadNum(4);
  context->SetThreadAffinity(0);
  auto cpu = std::make_shared<mindspore::CPUDeviceInfo>();
  cpu->SetEnableFP16(false);
  context->MutableDeviceInfo().push_back(cpu);
  mindspore::Model model;
  auto status = model.Build(argv[1], mindspore::ModelType::kMindIR_Lite, context);
  if (status != mindspore::kSuccess) { std::cerr << "Build failed: " << status << '\n'; return 3; }
  auto inputs = model.GetInputs();
  for (const auto &input : inputs) std::cerr << "INPUT " << input.Name() << " bytes=" << input.DataSize() << '\n';
  std::ofstream out(std::string(argv[2]) + "/lite_logits.bin", std::ios::binary);
  auto start = std::chrono::steady_clock::now();
  for (int row = 0; row < std::stoi(argv[3]); ++row) {
    for (auto &input : inputs) {
      std::string name = input.Name();
      std::string semantic;
      for (auto key : {"input_ids", "attention_mask", "token_type_ids"})
        if (name.find(key) != std::string::npos) semantic = key;
      if (semantic.empty()) throw std::runtime_error("Unexpected tensor name: " + name);
      std::string flat_path = std::string(argv[2]) + "/full_" + semantic + ".bin";
      std::ifstream probe(flat_path, std::ios::binary);
      bool flat = probe.good();
      probe.close();
      std::ifstream file(flat ? flat_path : std::string(argv[2]) + "/binary_inputs/" + std::to_string(row) + "/" + semantic + ".bin", std::ios::binary);
      if (flat) file.seekg(static_cast<std::streamoff>(row) * input.DataSize());
      if (!file.read(reinterpret_cast<char *>(input.MutableData()), input.DataSize())) throw std::runtime_error("Read failed");
    }
    std::vector<mindspore::MSTensor> outputs;
    status = model.Predict(inputs, &outputs);
    if (status != mindspore::kSuccess) { std::cerr << "Predict failed: " << status << '\n'; return 4; }
    if (outputs.size() != 1 || outputs[0].DataSize() != 12) throw std::runtime_error("Unexpected output shape");
    out.write(reinterpret_cast<const char *>(outputs[0].Data().get()), outputs[0].DataSize());
  }
  auto seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
  std::cout << "{\"samples\":" << argv[3] << ",\"elapsed_seconds\":" << seconds << "}\n";
  return 0;
}
