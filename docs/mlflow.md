# MLflow: Cơ sở lý thuyết, kiến trúc và thực hành

## 1. Mục tiêu tài liệu

Tài liệu này trình bày MLflow theo hướng lý thuyết kết hợp thực hành, giúp người học nắm được:

- MLflow là gì và vì sao công cụ này thường được dùng trong machine learning, deep learning, MLOps, LLMOps và hệ thống AI production.
- Các khái niệm cốt lõi như experiment, run, parameter, metric, tag, artifact, dataset, model, flavor, signature, model registry, model version và alias.
- Cách dùng MLflow Tracking để ghi lại thí nghiệm bằng `mlflow.start_run()`, `mlflow.log_param()`, `mlflow.log_metric()`, `mlflow.log_artifact()` và `mlflow.log_model()`.
- Cách chạy MLflow UI và MLflow Tracking Server ở local hoặc trong môi trường team.
- Cách cấu hình backend store và artifact store, ví dụ SQLite/PostgreSQL cho metadata và local filesystem/MinIO/S3 cho artifact.
- Cách đóng gói model theo chuẩn MLflow Model, dùng `pyfunc`, model signature và input example để phục vụ inference.
- Cách dùng Model Registry để quản lý vòng đời model, version, alias và metadata.
- Cách deploy model bằng MLflow Serving hoặc đóng gói Docker image.
- Cách dùng autologging, system metrics và evaluation.
- Cách MLflow liên hệ với PyTorch, FastAPI, PostgreSQL, MinIO, Docker, LangChain, LangGraph, vector database và các công nghệ trong repo này.
- Các lỗi thiết kế thường gặp khi dùng MLflow và cách tránh.

Tài liệu này tập trung vào MLflow 3.x và các workflow phổ biến cho machine learning truyền thống, deep learning và ứng dụng LLM/RAG ở mức tổng quan. Một số API, giao diện UI, Model Registry, GenAI tracing hoặc self-hosting option có thể thay đổi theo phiên bản, vì vậy khi làm dự án thực tế nên kiểm tra tài liệu chính thức đúng phiên bản `mlflow` đang dùng.

## 2. Tổng quan về MLflow

MLflow là nền tảng mã nguồn mở dùng để quản lý vòng đời machine learning và AI. MLflow giúp theo dõi thí nghiệm, lưu model, version hóa artifact, đánh giá model, quản lý model registry, triển khai inference server và quan sát workflow LLM/agent.

Một dự án machine learning thực tế thường không chỉ có một file notebook train model. Nó có nhiều vòng lặp:

```text
Chuẩn bị dữ liệu -> train model -> log metric -> lưu artifact -> đánh giá -> đăng ký model -> deploy -> theo dõi
```

Nếu không có công cụ quản lý, nhóm phát triển dễ gặp vấn đề:

- Không biết model tốt nhất được train bằng code nào.
- Không biết dataset version nào tạo ra checkpoint nào.
- Không nhớ hyperparameter của run tốt nhất.
- Không biết file model production nằm ở đâu.
- Không so sánh được nhiều lần thử nghiệm.
- Không tái lập được kết quả sau vài tuần.
- Không quản lý được quá trình promote model từ development sang production.

MLflow giải quyết các vấn đề này bằng một bộ thành phần thống nhất:

- **MLflow Tracking**: log experiment, run, parameter, metric, tag, artifact và model.
- **MLflow Models**: đóng gói model theo format chuẩn, có thể phục vụ inference qua nhiều môi trường.
- **Model Registry**: quản lý registered model, version, alias, tag và lifecycle.
- **MLflow Evaluation**: đánh giá model bằng metric, biểu đồ và custom evaluator.
- **MLflow Deployments/Serving**: chạy model như REST API hoặc đóng gói container.
- **MLflow GenAI**: tracing, evaluation, prompt management và observability cho LLM/agent.

MLflow thường được dùng cho:

- Experiment tracking.
- Model versioning.
- Artifact management.
- Model registry.
- Model serving.
- Batch inference.
- Hyperparameter comparison.
- Deep learning training tracking.
- RAG/LLM evaluation.
- Agent/LLM tracing.
- MLOps platform self-hosted.

### 2.1. Đặc điểm nổi bật

| Đặc điểm | Ý nghĩa |
| --- | --- |
| Open source | Có thể chạy local, self-host hoặc dùng qua managed platform. |
| Experiment tracking | Ghi lại parameter, metric, tag, artifact, source và model theo từng run. |
| Tracking UI | Giao diện để xem, lọc, so sánh và phân tích run. |
| Model format chuẩn | MLflow Model đóng gói model, dependency, signature, input example và flavor. |
| Pyfunc flavor | Interface chung để load/predict model từ nhiều framework khác nhau. |
| Model Registry | Quản lý model version, alias, tag, annotation và lineage. |
| Serving | Phục vụ model qua REST endpoint hoặc build Docker image. |
| Backend pluggable | Metadata có thể lưu ở SQLite, PostgreSQL, MySQL hoặc file store. |
| Artifact store pluggable | Artifact có thể lưu local, S3, MinIO, Azure Blob, GCS, v.v. |
| Autologging | Tự động log metric, parameter, model và artifact cho nhiều thư viện. |
| System metrics | Có thể log CPU, memory, GPU, network và disk usage. |
| Evaluation | Hỗ trợ đánh giá classification, regression và custom metric. |
| GenAI support | Có tracing, prompt management, evaluation và monitoring cho LLM/agent. |

## 3. Cơ sở lý thuyết

### 3.1. Experiment tracking

Experiment tracking là quá trình ghi lại thông tin của các lần thử nghiệm machine learning. Một thí nghiệm tốt không chỉ có accuracy cuối cùng, mà cần lưu:

- Hyperparameter.
- Dataset version.
- Code version.
- Environment.
- Metric theo thời gian.
- Model artifact.
- Evaluation output.
- Tag và ghi chú.
- Người chạy.
- Thời gian chạy.

MLflow Tracking tổ chức dữ liệu theo cấu trúc:

```text
Experiment
  -> Run
      -> Parameters
      -> Metrics
      -> Tags
      -> Artifacts
      -> Models
```

Nhờ vậy, ta có thể trả lời các câu hỏi:

- Run nào tốt nhất?
- Run đó dùng learning rate bao nhiêu?
- Model được lưu ở đâu?
- Run có artifact nào?
- Có thể load lại model để inference không?
- Model production đến từ run nào?

### 3.2. Experiment

Experiment là nhóm các run có cùng mục tiêu. Ví dụ:

```text
mnist-classifier
rag-docs-evaluation
house-price-regression
embedding-benchmark
```

Trong code:

```python
import mlflow

mlflow.set_experiment("mnist-classifier")
```

Nếu experiment chưa tồn tại, MLflow có thể tạo mới. Mỗi experiment có `experiment_id`, tên, artifact location và lifecycle stage.

Nên tạo experiment theo bài toán hoặc workflow rõ ràng. Không nên gom mọi thí nghiệm vào một experiment tên `test` hoặc `default`.

### 3.3. Run

Run là một lần thực thi training, evaluation, preprocessing, indexing, inference batch hoặc tracing workflow.

Ví dụ:

```python
import mlflow

mlflow.set_experiment("demo")

with mlflow.start_run(run_name="baseline"):
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_metric("accuracy", 0.91)
```

Một run thường có:

| Thành phần | Ý nghĩa |
| --- | --- |
| `run_id` | Định danh duy nhất của run. |
| `experiment_id` | Experiment chứa run. |
| `run_name` | Tên dễ đọc. |
| `params` | Hyperparameter hoặc cấu hình cố định. |
| `metrics` | Giá trị đo được theo thời gian. |
| `tags` | Metadata để lọc, ghi chú, phân loại. |
| `artifacts` | File, folder, model hoặc output được lưu. |
| `status` | `RUNNING`, `FINISHED`, `FAILED`, `KILLED`. |
| `start_time`, `end_time` | Thời gian chạy. |

### 3.4. Parameter

Parameter là giá trị cấu hình thường không thay đổi trong một run:

- `learning_rate`
- `batch_size`
- `epochs`
- `optimizer`
- `model_name`
- `seed`
- `chunk_size`
- `top_k`
- `embedding_model`

Ví dụ:

```python
params = {
    "learning_rate": 1e-3,
    "batch_size": 64,
    "epochs": 10,
    "optimizer": "Adam",
}

with mlflow.start_run():
    mlflow.log_params(params)
```

Không nên log loss hoặc accuracy vào parameter vì đó là metric thay đổi theo thời gian.

### 3.5. Metric

Metric là giá trị đo được trong quá trình chạy:

- `train_loss`
- `val_loss`
- `accuracy`
- `f1`
- `precision`
- `recall`
- `roc_auc`
- `latency_ms`
- `retrieval_recall_at_5`
- `answer_correctness`

Ví dụ:

```python
with mlflow.start_run():
    for epoch in range(10):
        train_loss = 1.0 / (epoch + 1)
        val_accuracy = 0.7 + epoch * 0.02

        mlflow.log_metric("train_loss", train_loss, step=epoch)
        mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)
```

MLflow lưu metric history, nghĩa là một metric có thể có nhiều giá trị theo step. Điều này giúp vẽ curve loss/accuracy qua epoch.

### 3.6. Tag

Tag là metadata dạng key-value dùng để mô tả run:

```python
with mlflow.start_run():
    mlflow.set_tag("stage", "debug")
    mlflow.set_tag("owner", "ml-team")
    mlflow.set_tag("model_family", "cnn")
```

Tag phù hợp cho:

- `baseline`
- `debug`
- `candidate`
- `production_candidate`
- `data_version`
- `git_branch`
- `owner`
- `task`

Parameter thường dùng để lưu cấu hình ảnh hưởng kết quả. Tag thường dùng để lọc, ghi chú hoặc phân loại run.

### 3.7. Artifact

Artifact là file hoặc thư mục được lưu cùng run:

- Checkpoint.
- Model file.
- Plot.
- Confusion matrix.
- Prediction CSV.
- Tokenizer.
- Label mapping.
- Dataset sample.
- Evaluation report.
- RAG output table.

Ví dụ:

```python
import mlflow

with mlflow.start_run():
    with open("metrics.txt", "w", encoding="utf-8") as f:
        f.write("accuracy=0.91\n")

    mlflow.log_artifact("metrics.txt")
```

Log cả thư mục:

```python
with mlflow.start_run():
    mlflow.log_artifacts("outputs", artifact_path="outputs")
```

Artifact lớn nên được lưu ở artifact store phù hợp như MinIO/S3 thay vì chỉ lưu trong thư mục local.

### 3.8. Dataset tracking

MLflow có thể ghi lại dataset input của run để hỗ trợ lineage. Ví dụ với pandas:

```python
import mlflow
import mlflow.data
import pandas as pd

df = pd.DataFrame(
    {
        "feature": [1, 2, 3],
        "label": [0, 1, 1],
    }
)

dataset = mlflow.data.from_pandas(
    df,
    source="local-demo",
    name="toy-dataset",
)

with mlflow.start_run():
    mlflow.log_input(dataset, context="training")
```

Trong dự án thật, dataset tracking giúp biết run nào dùng dữ liệu nào. Với dữ liệu lớn, nên lưu dữ liệu ở MinIO/S3/PostgreSQL/vector database và log metadata, URI hoặc fingerprint thay vì upload toàn bộ dữ liệu.

### 3.9. MLflow Model

MLflow Model là format chuẩn để đóng gói model. Một model được log thường là một thư mục có file `MLmodel` và các file đi kèm:

```text
model/
  MLmodel
  model.pkl
  conda.yaml
  python_env.yaml
  requirements.txt
  input_example.json
  serving_input_example.json
```

File `MLmodel` mô tả:

- Model được tạo khi nào.
- Run nào tạo ra model.
- MLflow version.
- Flavor nào được hỗ trợ.
- Signature input/output.
- Input example.
- Dependency.

MLflow Model giúp model không chỉ là file `.pkl` hoặc `.pt`, mà là một package có metadata và dependency để load, evaluate hoặc serve.

### 3.10. Flavor

Flavor là cách MLflow mô tả model theo framework hoặc interface:

| Flavor | Ý nghĩa |
| --- | --- |
| `python_function` / `pyfunc` | Interface chung `predict()` cho nhiều loại model. |
| `sklearn` | Model scikit-learn. |
| `pytorch` | Model PyTorch. |
| `tensorflow` | Model TensorFlow/Keras. |
| `xgboost` | Model XGBoost. |
| `lightgbm` | Model LightGBM. |
| `spark` | Spark ML model. |

Một model có thể có nhiều flavor. Ví dụ model scikit-learn có thể load bằng:

```python
model = mlflow.sklearn.load_model(model_uri)
```

hoặc load qua interface chung:

```python
model = mlflow.pyfunc.load_model(model_uri)
predictions = model.predict(data)
```

`pyfunc` rất quan trọng vì deployment tool có thể serve nhiều loại model thông qua một interface chung.

### 3.11. Model signature và input example

Model signature mô tả schema input/output của model:

- Tên cột.
- Kiểu dữ liệu.
- Shape tensor.
- Output schema.
- Inference parameter nếu có.

Ví dụ:

```python
from mlflow.models import infer_signature

signature = infer_signature(X_train, model.predict(X_train))
```

Khi log model:

```python
mlflow.sklearn.log_model(
    sk_model=model,
    name="model",
    signature=signature,
    input_example=X_train.head(3),
)
```

Signature giúp:

- Kiểm tra input khi serve model.
- Sinh ví dụ request cho inference.
- Giảm lỗi mismatch schema giữa training và serving.
- Giúp người khác hiểu model cần input gì.

### 3.12. Model Registry

Model Registry là nơi quản lý model đã đăng ký:

```text
Registered Model
  -> Version 1
  -> Version 2
  -> Version 3
```

Mỗi version có:

- Source model URI.
- Run tạo ra model.
- Metric.
- Tag.
- Alias.
- Description.
- Metadata.
- Lineage.

Registry giúp quản lý lifecycle:

```text
experiment run -> logged model -> registered model version -> alias -> deployment
```

Trong MLflow 3.x, alias là cách phổ biến để trỏ đến version có ý nghĩa:

```text
models:/fraud-detector@champion
models:/fraud-detector@challenger
```

Alias linh hoạt hơn việc hard-code version number trong deployment.

### 3.13. Tracking Server

Tracking Server là HTTP server cung cấp API và UI cho MLflow. Khi dùng local đơn giản, MLflow có thể ghi vào SQLite hoặc file store. Khi làm team, nên chạy tracking server để nhiều người log về một nơi.

```text
Client script -> MLflow Tracking Server -> Backend Store
                                      -> Artifact Store
```

Chạy server local:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

Trong code:

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("demo")
```

### 3.14. Backend store và artifact store

MLflow tách metadata và file lớn:

| Thành phần | Lưu gì | Ví dụ |
| --- | --- | --- |
| Backend store | Experiment, run, metric, param, tag, model registry metadata. | SQLite, PostgreSQL, MySQL, file store. |
| Artifact store | Model file, checkpoint, plot, CSV, image, report. | Local filesystem, S3, MinIO, Azure Blob, GCS. |

Ví dụ production self-host:

```text
MLflow Tracking Server
  -> Backend Store: PostgreSQL
  -> Artifact Store: MinIO/S3
```

Ví dụ command:

```bash
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri postgresql://user:password@postgres:5432/mlflow \
  --artifacts-destination s3://mlflow-artifacts
```

Với MinIO, cần cấu hình endpoint S3-compatible bằng environment variable.

## 4. Kiến trúc MLflow

### 4.1. Sơ đồ kiến trúc Mermaid

```mermaid
flowchart LR
    A[Training script / Notebook / Worker] --> B[MLflow Python SDK]
    B --> C[Tracking Server]
    C --> D[Backend Store]
    C --> E[Artifact Store]
    C --> F[MLflow UI]
    C --> G[Model Registry]

    D[(SQLite / PostgreSQL / MySQL)]
    E[(Local FS / MinIO / S3 / GCS / Azure Blob)]

    G --> H[Model Version]
    H --> I[Alias: champion / challenger]
    I --> J[Serving / Batch Inference]

    K[LLM / Agent App] --> B
    B --> L[Traces / Evaluation / Prompts]
```

Luồng chính:

1. Script gọi `mlflow.set_experiment()` và `mlflow.start_run()`.
2. SDK log parameter, metric, tag, artifact và model.
3. Tracking Server ghi metadata vào backend store.
4. Artifact được lưu vào artifact store.
5. MLflow UI đọc dữ liệu để hiển thị experiment/run/model.
6. Model quan trọng được đăng ký vào Registry.
7. Deployment dùng model URI hoặc alias để load/serve model.

### 4.2. Các thành phần quan trọng

| Thành phần | Vai trò |
| --- | --- |
| MLflow SDK | API Python/R/Java/REST để log và truy vấn dữ liệu. |
| Tracking Server | HTTP server phục vụ API và UI. |
| Tracking UI | Giao diện xem experiment, run, metric, artifact và model. |
| Backend Store | Lưu metadata có cấu trúc. |
| Artifact Store | Lưu file và model artifact. |
| MLflow Model | Format đóng gói model, dependency, flavor và schema. |
| Model Registry | Quản lý registered model, version, alias và metadata. |
| MLflow Serving | Serve model qua REST endpoint. |
| MLflow Evaluation | Đánh giá model và log kết quả. |
| GenAI Tracing | Trace LLM/agent, prompt, tool call và retrieval. |

### 4.3. Local mode, server mode và production mode

| Chế độ | Mô tả | Khi nào dùng |
| --- | --- | --- |
| Local mode | Log vào local backend/artifact store. | Học, notebook cá nhân, thử nhanh. |
| Server mode | Chạy `mlflow server` để nhiều client log chung. | Team nhỏ, lab, demo. |
| Production mode | Tracking Server + PostgreSQL/MySQL + MinIO/S3 + auth/network security. | Dự án thật, nhiều user, model lifecycle. |

Local nhanh:

```bash
mlflow server --port 5000
```

Client:

```python
mlflow.set_tracking_uri("http://localhost:5000")
```

Production nên chú ý:

- Không expose tracking server public nếu chưa có bảo mật.
- Dùng database thật thay vì file store cho concurrency.
- Dùng artifact store bền vững.
- Cấu hình `--allowed-hosts` và CORS khi mở ra mạng.
- Backup database và artifact store.

## 5. Vòng đời một thí nghiệm với MLflow

### 5.1. Luồng training run

```mermaid
sequenceDiagram
    participant User as Người dùng
    participant Script as train.py
    participant SDK as MLflow SDK
    participant Server as Tracking Server
    participant Store as Backend/Artifact Store
    participant UI as MLflow UI

    User->>Script: Chạy training script
    Script->>SDK: set_experiment()
    Script->>SDK: start_run()
    SDK->>Server: Tạo run metadata
    Server->>Store: Lưu run
    Script->>SDK: log_params()
    loop Mỗi epoch
        Script->>Script: Train / validate
        Script->>SDK: log_metric(step=epoch)
        SDK->>Server: Gửi metric
        Server->>Store: Lưu metric history
    end
    Script->>SDK: log_model() / log_artifact()
    Server->>Store: Lưu artifact/model
    Script->>SDK: end_run()
    UI->>Server: Đọc run để hiển thị
```

### 5.2. Luồng model registry

```mermaid
flowchart TD
    A[Training run] --> B[Logged MLflow Model]
    B --> C[Register model]
    C --> D[Registered Model: fraud-detector]
    D --> E[Version 1]
    D --> F[Version 2]
    F --> G[Alias: challenger]
    E --> H[Alias: champion]
    H --> I[Production serving]
    G --> J[Shadow evaluation]
```

Model Registry giúp tách rõ:

- Run sinh ra model.
- Model package được lưu ở đâu.
- Version nào đang được dùng.
- Version nào là challenger.
- Version nào đã qua kiểm thử.

### 5.3. Luồng serving

```mermaid
flowchart LR
    A[Model URI] --> B[mlflow models serve]
    B --> C[Inference Server]
    C --> D[/invocations]
    C --> E[/ping]
    C --> F[/health]
    C --> G[/version]
    H[Client / FastAPI / Batch Job] --> D
    D --> I[Predictions]
```

Ví dụ:

```bash
mlflow models serve -m runs:/<run_id>/model -p 5000
```

Gọi inference:

```bash
curl http://127.0.0.1:5000/invocations \
  -H "Content-Type: application/json" \
  --data "{\"inputs\": [[1, 2], [3, 4]]}"
```

## 6. Các khái niệm cốt lõi

### 6.1. `mlflow.set_tracking_uri()`

`set_tracking_uri()` cấu hình nơi client gửi log:

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
```

Có thể dùng environment variable:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

PowerShell:

```powershell
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
```

Nếu không cấu hình, MLflow dùng default backend local theo phiên bản và môi trường đang chạy.

### 6.2. `mlflow.set_experiment()`

Chọn experiment:

```python
mlflow.set_experiment("rag-evaluation")
```

Nên gọi trước `start_run()`.

### 6.3. `mlflow.start_run()`

Tạo run mới:

```python
with mlflow.start_run(run_name="baseline") as run:
    print(run.info.run_id)
```

Nếu không dùng context manager, cần end run:

```python
run = mlflow.start_run()
mlflow.log_metric("loss", 0.5)
mlflow.end_run()
```

Nên ưu tiên context manager để tránh run bị treo ở trạng thái chưa kết thúc.

### 6.4. `mlflow.log_param()` và `mlflow.log_params()`

Log một parameter:

```python
mlflow.log_param("learning_rate", 0.001)
```

Log nhiều parameter:

```python
mlflow.log_params(
    {
        "batch_size": 64,
        "epochs": 10,
        "optimizer": "AdamW",
    }
)
```

### 6.5. `mlflow.log_metric()` và `mlflow.log_metrics()`

Log một metric:

```python
mlflow.log_metric("accuracy", 0.91)
```

Log theo step:

```python
mlflow.log_metric("train_loss", 0.42, step=3)
```

Log nhiều metric:

```python
mlflow.log_metrics(
    {
        "val_loss": 0.31,
        "val_accuracy": 0.93,
    },
    step=3,
)
```

### 6.6. `mlflow.set_tag()` và `mlflow.set_tags()`

```python
mlflow.set_tag("stage", "debug")
mlflow.set_tags(
    {
        "owner": "ml-team",
        "model_family": "resnet",
    }
)
```

Tags giúp search run:

```python
from mlflow import MlflowClient

client = MlflowClient()
runs = client.search_runs(
    experiment_ids=["1"],
    filter_string="tags.stage = 'debug'",
)
```

### 6.7. `mlflow.log_artifact()` và `mlflow.log_artifacts()`

```python
mlflow.log_artifact("confusion_matrix.png")
mlflow.log_artifacts("reports", artifact_path="reports")
```

`artifact_path` giúp tổ chức file trong run:

```text
artifacts/
  reports/
    report.html
  plots/
    loss.png
  predictions/
    output.csv
```

### 6.8. `mlflow.<flavor>.log_model()`

Log model theo flavor:

```python
import mlflow.sklearn

model_info = mlflow.sklearn.log_model(
    sk_model=model,
    name="model",
)
```

`model_info.model_uri` có thể dùng để load lại:

```python
loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)
predictions = loaded_model.predict(X_test)
```

### 6.9. `mlflow.pyfunc`

`pyfunc` là interface chung:

```python
model = mlflow.pyfunc.load_model("runs:/<run_id>/model")
predictions = model.predict(data)
```

Khi deploy bằng MLflow Serving, hệ thống thường gọi model qua pyfunc. Vì vậy model signature và input example nên được log cẩn thận.

### 6.10. `MlflowClient`

`MlflowClient` dùng để thao tác programmatic với experiment, run, model registry:

```python
from mlflow import MlflowClient

client = MlflowClient()
experiment = client.get_experiment_by_name("demo")
runs = client.search_runs([experiment.experiment_id])
```

Use case:

- Tìm run tốt nhất.
- Cập nhật tag.
- Tạo registered model.
- Gán alias cho model version.
- Tự động promote model sau evaluation.

### 6.11. Autologging

Autologging giúp tự động log parameter, metric, model, signature và artifact cho nhiều thư viện:

```python
import mlflow

mlflow.autolog()

with mlflow.start_run():
    model.fit(X_train, y_train)
```

Hoặc bật cho thư viện cụ thể:

```python
mlflow.sklearn.autolog()
mlflow.pytorch.autolog()
```

Autologging rất tiện khi bắt đầu nhanh, nhưng trong production thường vẫn nên log thủ công các metric nghiệp vụ quan trọng để kiểm soát rõ ràng.

### 6.12. System metrics

MLflow có thể log CPU, memory, GPU, network và disk usage:

```python
import mlflow

with mlflow.start_run(log_system_metrics=True):
    train_model()
```

Hoặc bật toàn cục:

```python
mlflow.enable_system_metrics_logging()
```

Cần cài thêm dependency:

```bash
pip install psutil
pip install nvidia-ml-py
```

Metric hệ thống thường có prefix `system/`, ví dụ:

```text
system/cpu_utilization_percentage
system/gpu_memory_usage_megabytes
```

## 7. Cài đặt và cấu hình

### 7.1. Cài MLflow

```bash
pip install mlflow
```

Kiểm tra version:

```bash
python -c "import mlflow; print(mlflow.__version__)"
```

Nếu cần PostgreSQL backend:

```bash
pip install psycopg2-binary
```

Nếu cần S3/MinIO artifact store:

```bash
pip install boto3
```

### 7.2. Chạy MLflow UI/Server local

```bash
mlflow server --host 127.0.0.1 --port 5000
```

Mở:

```text
http://127.0.0.1:5000
```

Trong code:

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("local-demo")
```

### 7.3. Cấu hình bằng biến môi trường

Các biến thường dùng:

| Biến | Ý nghĩa |
| --- | --- |
| `MLFLOW_TRACKING_URI` | Tracking server URI. |
| `MLFLOW_EXPERIMENT_NAME` | Experiment mặc định. |
| `MLFLOW_TRACKING_USERNAME` | Username nếu server dùng basic auth. |
| `MLFLOW_TRACKING_PASSWORD` | Password nếu server dùng basic auth. |
| `MLFLOW_TRACKING_TOKEN` | Token nếu dùng auth token. |
| `MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING` | Bật/tắt system metrics. |
| `MLFLOW_S3_ENDPOINT_URL` | Endpoint S3-compatible, ví dụ MinIO. |
| `AWS_ACCESS_KEY_ID` | Access key cho S3/MinIO. |
| `AWS_SECRET_ACCESS_KEY` | Secret key cho S3/MinIO. |
| `AWS_DEFAULT_REGION` | Region cho S3-compatible client. |

Ví dụ `.env` local:

```env
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
MLFLOW_EXPERIMENT_NAME=sql-nosql-ai-lab
MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING=true
```

Không commit `.env` chứa password, token hoặc secret key.

### 7.4. PostgreSQL backend store

Tạo database `mlflow`, sau đó chạy:

```bash
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri postgresql://mlflow:mlflow@localhost:5432/mlflow \
  --default-artifact-root ./mlartifacts
```

Trong Docker Compose, hostname PostgreSQL thường là tên service:

```text
postgresql://mlflow:mlflow@postgres:5432/mlflow
```

Production nên dùng PostgreSQL/MySQL thay vì file store vì:

- Nhiều client ghi đồng thời tốt hơn.
- Backup rõ ràng hơn.
- Registry metadata ổn định hơn.
- Dễ quản trị quyền và migration hơn.

### 7.5. MinIO/S3 artifact store

Ví dụ cấu hình MinIO:

```bash
export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
```

Chạy server:

```bash
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri postgresql://mlflow:mlflow@localhost:5432/mlflow \
  --artifacts-destination s3://mlflow-artifacts
```

Lưu ý:

- Bucket `mlflow-artifacts` cần tồn tại hoặc hệ thống cần quyền tạo bucket tùy cấu hình.
- Client và server đều cần truy cập artifact store nếu không dùng artifact proxy phù hợp.
- Không hard-code access key trong code.

### 7.6. Cấu trúc project gợi ý

```text
project/
  train.py
  evaluate.py
  serve.py
  configs/
    baseline.yaml
  data/
    .gitkeep
  outputs/
    .gitkeep
  models/
    .gitkeep
  mlruns/
  mlartifacts/
```

`.gitignore`:

```gitignore
mlruns/
mlartifacts/
outputs/
models/
.env
*.db
```

## 8. Ví dụ sử dụng MLflow cơ bản

### 8.1. Log parameter và metric đơn giản

```python
import random
import mlflow

mlflow.set_experiment("basic-demo")

with mlflow.start_run(run_name="manual-logging"):
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("batch_size", 64)

    loss = 1.0
    for epoch in range(10):
        loss *= 0.8 + random.random() * 0.05
        accuracy = 1.0 - loss

        mlflow.log_metric("train_loss", loss, step=epoch)
        mlflow.log_metric("val_accuracy", accuracy, step=epoch)

    mlflow.set_tag("stage", "demo")
```

Chạy UI:

```bash
mlflow server --port 5000
```

### 8.2. Scikit-learn với autologging

```python
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

mlflow.set_experiment("sklearn-autolog-demo")
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="logistic-regression"):
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
```

Autologging sẽ tự log parameter, metric và model tùy framework.

### 8.3. Scikit-learn log thủ công

```python
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

params = {
    "max_iter": 1000,
    "solver": "lbfgs",
    "random_state": 42,
}

mlflow.set_experiment("sklearn-manual-demo")

with mlflow.start_run(run_name="iris-lr") as run:
    mlflow.log_params(params)

    model = LogisticRegression(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
    mlflow.log_metric("f1_macro", f1_score(y_test, y_pred, average="macro"))

    signature = infer_signature(X_test, y_pred)
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        name="model",
        signature=signature,
        input_example=X_test.head(3),
    )

    print(run.info.run_id)
    print(model_info.model_uri)
```

### 8.4. Load model để inference

```python
import mlflow.pyfunc

model_uri = "runs:/<run_id>/model"
model = mlflow.pyfunc.load_model(model_uri)

predictions = model.predict(X_test)
print(predictions[:5])
```

Nếu muốn load native scikit-learn model:

```python
import mlflow.sklearn

model = mlflow.sklearn.load_model(model_uri)
predictions = model.predict(X_test)
```

### 8.5. Log artifact

```python
import json
import mlflow

report = {
    "accuracy": 0.91,
    "f1_macro": 0.9,
}

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with mlflow.start_run():
    mlflow.log_artifact("report.json", artifact_path="reports")
```

### 8.6. Log dataset input

```python
import mlflow
import mlflow.data
import pandas as pd

df = pd.DataFrame(
    {
        "text": ["Redis là cache", "PostgreSQL là database"],
        "label": ["cache", "database"],
    }
)

dataset = mlflow.data.from_pandas(
    df,
    source="docs-example",
    name="text-classification-demo",
)

with mlflow.start_run():
    mlflow.log_input(dataset, context="training")
```

### 8.7. Evaluate model

```python
import mlflow

eval_data = X_test.copy()
eval_data["label"] = y_test

with mlflow.start_run():
    result = mlflow.models.evaluate(
        model_uri,
        eval_data,
        targets="label",
        model_type="classifier",
    )

    print(result.metrics)
```

MLflow có thể tự sinh metric và artifact như confusion matrix, ROC curve hoặc classification report tùy loại model và dữ liệu.

## 9. MLflow trong PyTorch

### 9.1. Những gì nên log

Trong PyTorch, nên log:

| Nhóm | Nội dung |
| --- | --- |
| Params | `learning_rate`, `batch_size`, `epochs`, `optimizer`, `scheduler`, `model_name`, `seed`. |
| Metrics | `train_loss`, `val_loss`, `accuracy`, `f1`, `learning_rate`, `grad_norm`. |
| Artifacts | Checkpoint, confusion matrix, prediction CSV, label mapping. |
| Model | MLflow PyTorch model hoặc pyfunc wrapper. |
| Tags | `stage`, `owner`, `model_family`, `dataset_version`. |
| System metrics | CPU/GPU utilization, memory. |

Không nên log:

- Tensor lớn ở mỗi batch.
- Checkpoint ở mọi step nếu không cần.
- Dữ liệu nhạy cảm hoặc secret.
- Metric key động theo sample id.

### 9.2. Training loop PyTorch tối giản

```python
import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class Classifier(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=32, num_classes=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x):
        return self.net(x)


x = torch.randn(1000, 10)
y = (x.sum(dim=1) > 0).long()
loader = DataLoader(TensorDataset(x, y), batch_size=64, shuffle=True)

params = {
    "epochs": 5,
    "batch_size": 64,
    "learning_rate": 1e-3,
    "hidden_dim": 32,
}

mlflow.set_experiment("pytorch-demo")

with mlflow.start_run(run_name="mlp") as run:
    mlflow.log_params(params)

    model = Classifier(hidden_dim=params["hidden_dim"])
    optimizer = torch.optim.Adam(model.parameters(), lr=params["learning_rate"])
    criterion = nn.CrossEntropyLoss()

    for epoch in range(params["epochs"]):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for x_batch, y_batch in loader:
            optimizer.zero_grad()
            logits = model(x_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * x_batch.size(0)
            pred = logits.argmax(dim=1)
            correct += (pred == y_batch).sum().item()
            total += x_batch.size(0)

        mlflow.log_metric("train_loss", total_loss / total, step=epoch)
        mlflow.log_metric("train_accuracy", correct / total, step=epoch)

    mlflow.pytorch.log_model(model, name="model")
```

### 9.3. Best checkpoint

```python
import torch
import mlflow

best_val_loss = float("inf")

with mlflow.start_run():
    for epoch in range(epochs):
        train_loss = train_one_epoch()
        val_loss = evaluate()

        mlflow.log_metric("train_loss", train_loss, step=epoch)
        mlflow.log_metric("val_loss", val_loss, step=epoch)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_loss": val_loss,
                },
                "best_checkpoint.pt",
            )
            mlflow.log_metric("best_val_loss", best_val_loss)
            mlflow.log_artifact("best_checkpoint.pt", artifact_path="checkpoints")
```

Nếu cần deploy bằng MLflow Serving, nên log model bằng `mlflow.pytorch.log_model()` hoặc custom `pyfunc` thay vì chỉ log checkpoint `.pt`.

### 9.4. Log model với signature

```python
from mlflow.models import infer_signature

model.eval()
input_example = torch.randn(3, 10)

with torch.no_grad():
    output_example = model(input_example).numpy()

signature = infer_signature(input_example.numpy(), output_example)

with mlflow.start_run():
    mlflow.pytorch.log_model(
        pytorch_model=model,
        name="model",
        signature=signature,
        input_example=input_example.numpy(),
    )
```

Signature giúp MLflow Serving kiểm tra input tốt hơn.

### 9.5. Autologging cho PyTorch

```python
import mlflow

mlflow.pytorch.autolog()

with mlflow.start_run():
    train_model()
```

Autologging có thể tiết kiệm thời gian khi thử nghiệm. Tuy nhiên với training loop tự viết phức tạp, log thủ công vẫn rõ ràng hơn vì ta kiểm soát metric, step và artifact.

## 10. MLflow Model Registry

### 10.1. Đăng ký model

Cách 1: register ngay khi log model:

```python
with mlflow.start_run():
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        name="model",
        registered_model_name="iris-classifier",
    )
```

Cách 2: register từ model URI:

```python
model_uri = "runs:/<run_id>/model"
mlflow.register_model(model_uri, "iris-classifier")
```

### 10.2. Load model từ Registry

Load theo version:

```python
model = mlflow.pyfunc.load_model("models:/iris-classifier/1")
```

Load theo alias:

```python
model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
```

Alias giúp deployment không cần sửa code khi promote version mới. Chỉ cần đổi alias trong registry.

### 10.3. Gán alias bằng `MlflowClient`

```python
from mlflow import MlflowClient

client = MlflowClient()
client.set_registered_model_alias(
    name="iris-classifier",
    alias="champion",
    version="1",
)
```

Sau đó:

```python
model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
```

### 10.4. Tags và metadata

```python
client.set_model_version_tag(
    name="iris-classifier",
    version="1",
    key="validation_status",
    value="passed",
)
```

Gợi ý tags:

| Tag | Ý nghĩa |
| --- | --- |
| `validation_status` | `passed`, `failed`, `pending`. |
| `owner` | Người hoặc team chịu trách nhiệm. |
| `dataset_version` | Dataset dùng để train. |
| `risk_level` | Mức rủi ro model. |
| `deployment_target` | API, batch, edge, mobile. |

### 10.5. Champion và challenger

Pattern phổ biến:

```text
champion: version đang phục vụ production
challenger: version mới đang so sánh
candidate: version chuẩn bị review
archived: version không còn dùng
```

Workflow:

```text
Train model -> log model -> evaluate -> register -> gán alias candidate
  -> kiểm thử -> gán alias challenger -> shadow test -> gán alias champion
```

## 11. MLflow Serving và deployment

### 11.1. Serve model local

```bash
mlflow models serve -m runs:/<run_id>/model -p 5000
```

Gọi endpoint:

```bash
curl http://127.0.0.1:5000/invocations \
  -H "Content-Type: application/json" \
  --data "{\"inputs\": [[5.1, 3.5, 1.4, 0.2]]}"
```

Các endpoint chính:

| Endpoint | Ý nghĩa |
| --- | --- |
| `/invocations` | Nhận input và trả prediction. |
| `/ping` | Health check. |
| `/health` | Health check tương tự. |
| `/version` | Trả version MLflow. |

### 11.2. Serve model từ Registry

```bash
mlflow models serve -m "models:/iris-classifier@champion" -p 5000
```

Ưu điểm:

- Code deployment không cần biết run id.
- Có thể đổi champion version từ registry.
- Phù hợp với CI/CD và promotion workflow.

### 11.3. Batch inference

```python
import pandas as pd
import mlflow.pyfunc

model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")
data = pd.read_csv("input.csv")
predictions = model.predict(data)
predictions.to_csv("output.csv", index=False)
```

Hoặc dùng CLI:

```bash
mlflow models predict \
  -m "models:/iris-classifier@champion" \
  -i input.csv \
  -o output.csv
```

### 11.4. Build Docker image

```bash
mlflow models build-docker \
  -m "models:/iris-classifier@champion" \
  -n iris-classifier:latest
```

Sau đó chạy container:

```bash
docker run -p 5000:8080 iris-classifier:latest
```

Docker image hữu ích khi cần deploy lên Kubernetes, cloud service hoặc hệ thống inference nội bộ.

### 11.5. FastAPI wrapper

Trong nhiều hệ thống backend, thay vì expose trực tiếp MLflow Serving, ta có thể dùng FastAPI làm lớp API nghiệp vụ:

```python
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = mlflow.pyfunc.load_model("models:/iris-classifier@champion")


class PredictRequest(BaseModel):
    rows: list[list[float]]


@app.post("/predict")
def predict(request: PredictRequest):
    data = pd.DataFrame(request.rows)
    predictions = model.predict(data)
    return {"predictions": predictions.tolist()}
```

FastAPI phù hợp khi cần:

- Authentication/authorization.
- Input validation nâng cao.
- Rate limit.
- Logging request.
- Business logic trước/sau inference.
- Kết nối database.

## 12. MLflow trong hệ thống RAG và LLM

### 12.1. Tracking cho RAG evaluation

Với RAG, MLflow có thể log:

- Dataset câu hỏi.
- Prompt version.
- Chunk size.
- Chunk overlap.
- Embedding model.
- Vector database.
- Collection name.
- Retriever top-k.
- Reranker.
- LLM model.
- Retrieval metric.
- Answer quality metric.
- Latency.
- Evaluation artifact.

Ví dụ:

```python
import json
import mlflow

params = {
    "embedding_model": "text-embedding-model",
    "chunk_size": 800,
    "chunk_overlap": 100,
    "vector_store": "qdrant",
    "top_k": 5,
    "llm": "chat-model",
}

with mlflow.start_run(run_name="rag-eval"):
    mlflow.log_params(params)
    mlflow.log_metric("retrieval_recall_at_5", 0.82)
    mlflow.log_metric("answer_correctness", 0.76)
    mlflow.log_metric("avg_latency_ms", 1240)

    with open("rag_predictions.json", "w", encoding="utf-8") as f:
        json.dump(eval_rows, f, ensure_ascii=False, indent=2)

    mlflow.log_artifact("rag_predictions.json", artifact_path="evaluation")
```

### 12.2. GenAI tracing

MLflow GenAI có tracing cho LLM/agent/RAG. Trace thường ghi lại:

- Prompt.
- LLM request/response.
- Retriever input/output.
- Tool call.
- Chain/graph step.
- Latency.
- Error.
- Metadata.

Ví dụ ý tưởng:

```python
import mlflow

with mlflow.start_span(name="retrieval") as span:
    span.set_inputs({"question": question})
    docs = retriever.invoke(question)
    span.set_outputs({"num_docs": len(docs)})
```

Tracing phù hợp khi cần debug runtime:

```text
User question -> rewrite query -> retrieve docs -> rerank -> generate answer -> evaluate
```

### 12.3. MLflow và LangChain/LangGraph

Trong hệ thống LangChain/LangGraph:

- MLflow Tracking có thể log evaluation batch.
- MLflow GenAI tracing có thể quan sát từng LLM call hoặc tool call.
- Model Registry có thể quản lý version của chain, pyfunc model hoặc external model.
- Artifact store có thể lưu prompt file, eval dataset và output.

Với workflow nhiều node:

```text
LangGraph node A -> retrieve
LangGraph node B -> rerank
LangGraph node C -> generate
LangGraph node D -> grade
```

Ta có thể log:

- Metric tổng hợp bằng MLflow Tracking.
- Trace chi tiết bằng MLflow GenAI.
- Prompt version bằng prompt management nếu cần.

### 12.4. Khi nào dùng MLflow GenAI thay vì Tracking thường

| Nhu cầu | Công cụ phù hợp |
| --- | --- |
| Log metric batch evaluation | MLflow Tracking. |
| Log model checkpoint | MLflow Models/Artifacts. |
| Quản lý model version | Model Registry. |
| Trace từng request LLM | MLflow GenAI Tracing. |
| Đánh giá LLM bằng scorer/judge | MLflow GenAI Evaluation. |
| Debug agent tool call | MLflow GenAI Tracing. |

## 13. MLflow trong hệ thống backend

### 13.1. Kiến trúc FastAPI + worker + MLflow

Không nên train model trực tiếp trong request API đồng bộ. Nên tách:

```mermaid
flowchart LR
    A[FastAPI] --> B[PostgreSQL: job metadata]
    A --> C[Queue / Background Worker]
    C --> D[Training / Evaluation Script]
    D --> E[MLflow Tracking Server]
    E --> F[Backend Store: PostgreSQL]
    E --> G[Artifact Store: MinIO]
    E --> H[Model Registry]
    A --> I[Return job id]
```

FastAPI lưu:

- `job_id`
- `user_id`
- `status`
- `mlflow_run_id`
- `mlflow_experiment_id`
- `mlflow_run_url`
- `registered_model_name`
- `model_version`
- `created_at`
- `finished_at`

Worker chịu trách nhiệm:

- Train/evaluate.
- Log MLflow run.
- Log model/artifact.
- Register model nếu đạt điều kiện.
- Cập nhật job status trong PostgreSQL.

### 13.2. Service layer gợi ý

```python
from dataclasses import dataclass
import mlflow


@dataclass
class TrainingConfig:
    experiment_name: str
    run_name: str
    learning_rate: float
    batch_size: int
    epochs: int


def run_training(config: TrainingConfig) -> str:
    mlflow.set_experiment(config.experiment_name)

    with mlflow.start_run(run_name=config.run_name) as run:
        mlflow.log_params(config.__dict__)

        for epoch in range(config.epochs):
            metrics = train_one_epoch()
            mlflow.log_metrics(metrics, step=epoch)

        return run.info.run_id
```

### 13.3. Docker Compose gợi ý

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: mlflow
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  mlflow:
    image: ghcr.io/mlflow/mlflow
    ports:
      - "5000:5000"
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
    command:
      - mlflow
      - server
      - --host
      - 0.0.0.0
      - --port
      - "5000"
      - --backend-store-uri
      - postgresql://mlflow:mlflow@postgres:5432/mlflow
      - --artifacts-destination
      - s3://mlflow-artifacts
    depends_on:
      - postgres
      - minio

volumes:
  postgres_data:
  minio_data:
```

Ghi chú: cần tạo bucket `mlflow-artifacts` hoặc bổ sung service init bucket tùy môi trường.

### 13.4. CI/CD model promotion

Một workflow đơn giản:

```text
Train -> log run -> evaluate -> nếu metric đạt ngưỡng -> register model
  -> set alias challenger -> deploy staging -> smoke test
  -> set alias champion -> deploy production
```

Tiêu chí tự động:

- `accuracy >= 0.92`
- `f1_macro >= 0.9`
- `latency_p95_ms <= 200`
- Không vi phạm data drift rule.
- Evaluation dataset đúng version.

## 14. MLflow và các công nghệ trong repo này

| Công nghệ | Cách MLflow có thể liên hệ |
| --- | --- |
| PyTorch | Log metric, checkpoint, model, signature, input example và system metrics. |
| FastAPI | Expose API tạo job hoặc serve model qua wrapper nghiệp vụ. |
| PostgreSQL | Là backend store cho MLflow hoặc lưu metadata job nghiệp vụ. |
| Redis | Queue nhẹ, cache trạng thái job, rate limit request inference. |
| MinIO | Artifact store S3-compatible cho model, checkpoint, report, dataset. |
| Qdrant/Milvus | Log config vector store, collection, embedding model và retrieval metric. |
| Elasticsearch | Log search/ranking experiment, analyzer config, relevance metric. |
| LangChain | Log RAG evaluation, chain config, prompt version, trace hoặc output artifact. |
| LangGraph | Log workflow evaluation hoặc trace từng node trong agent graph. |
| Docker | Chạy MLflow server, trainer, worker hoặc model serving container. |

Ví dụ pipeline RAG:

```text
docs/*.md
  -> preprocessing/chunking
  -> embedding
  -> Qdrant/Milvus
  -> RAG evaluation
  -> MLflow Tracking: params + metrics + artifacts
  -> Model Registry: chain/model version nếu cần deploy
```

Thông tin nên log:

- `chunk_size`
- `chunk_overlap`
- `embedding_model`
- `vector_db`
- `collection_name`
- `top_k`
- `reranker`
- `llm_model`
- `prompt_version`
- `eval_dataset_version`
- `retrieval_recall_at_k`
- `answer_correctness`
- `avg_latency_ms`

## 15. So sánh MLflow với công cụ khác

### 15.1. MLflow và W&B

| Tiêu chí | MLflow | W&B |
| --- | --- | --- |
| Mã nguồn mở/self-host | Rất mạnh, phổ biến trong self-host MLOps. | Có cloud mạnh, cũng có lựa chọn enterprise/private. |
| Experiment tracking | Có. | Có, UI rất mạnh cho cộng tác và visualization. |
| Artifact/model management | Có MLflow Models, artifact store, registry. | Có Artifacts, Registry. |
| Model serving | Có `mlflow models serve`, Docker, deployment tooling. | Không phải trọng tâm chính như MLflow Serving. |
| Registry | Có Model Registry với version/alias. | Có Registry theo artifact collection. |
| GenAI tracing | Có MLflow GenAI. | Có W&B Weave. |
| Dễ bắt đầu local | Rất dễ, không cần account. | Cần account nếu dùng cloud online; có offline mode. |

MLflow phù hợp nếu muốn open-source/self-host và model lifecycle đầy đủ. W&B rất mạnh nếu ưu tiên dashboard cloud, collaboration và experiment visualization hiện đại.

### 15.2. MLflow và TensorBoard

| Tiêu chí | MLflow | TensorBoard |
| --- | --- | --- |
| Tracking parameter/metric | Có. | Có metric visualization nhưng param/artifact lifecycle không phải trọng tâm. |
| Model Registry | Có. | Không. |
| Model packaging | Có MLflow Models. | Không. |
| Serving | Có. | Không. |
| Deep learning visualization | Đủ dùng. | Mạnh cho graph, scalar, histogram, embedding projector. |
| Self-host team workflow | Có Tracking Server. | Thường local hoặc setup riêng. |

TensorBoard phù hợp để debug training deep learning. MLflow phù hợp để quản lý vòng đời thí nghiệm và model.

### 15.3. MLflow và LangSmith

| Tiêu chí | MLflow | LangSmith |
| --- | --- | --- |
| ML training tracking | Mạnh. | Không phải trọng tâm chính. |
| Model Registry | Có. | Không phải trọng tâm chính. |
| LLM/agent tracing | Có MLflow GenAI. | Rất mạnh trong hệ sinh thái LangChain/LangGraph. |
| RAG evaluation | Có thể dùng Tracking/GenAI Evaluation. | Mạnh cho tracing/eval LangChain. |
| Self-host/open-source | MLflow là open-source platform phổ biến. | Tùy sản phẩm/dịch vụ. |

Nếu dự án chủ yếu là model training và model deployment, MLflow rất phù hợp. Nếu dự án chủ yếu là LangChain/LangGraph agent, LangSmith hoặc MLflow GenAI đều đáng cân nhắc tùy stack.

### 15.4. MLflow và tự lưu CSV/checkpoint

| Cách làm thủ công | MLflow |
| --- | --- |
| CSV metric rời rạc. | Metric history có UI và search. |
| Checkpoint không rõ nguồn gốc. | Model artifact gắn với run/param/metric. |
| Không có registry. | Có Model Registry. |
| Khó share. | Có Tracking UI. |
| Khó deploy thống nhất. | Có MLflow Model format và serving. |

Với bài tập nhỏ, CSV có thể đủ. Với dự án nhiều thí nghiệm hoặc nhiều người, MLflow giúp giảm hỗn loạn đáng kể.

## 16. Thiết kế project MLflow

### 16.1. Đặt tên experiment

Nên:

```text
rag-docs-eval
pytorch-classifier
embedding-benchmark
fraud-detection
```

Không nên:

```text
test
demo
default
experiment
```

### 16.2. Đặt tên run

Tên run nên giúp đọc bảng nhanh:

```python
with mlflow.start_run(run_name="resnet18-lr1e-3-bs64"):
    ...
```

Không cần nhét mọi config vào tên run vì params đã lưu đầy đủ.

### 16.3. Naming metric

Nên dùng tên ổn định:

```text
train_loss
val_loss
val_accuracy
f1_macro
latency_ms
retrieval_recall_at_5
```

Tránh:

```text
loss user 123
loss-user-123
accuracy@today
metric_2026_06_11_10_30
```

Metric key động làm search và chart rối.

### 16.4. Parameter và tag strategy

Parameter:

```text
learning_rate
batch_size
epochs
optimizer
model_name
dataset_version
seed
```

Tag:

```text
stage
owner
task
branch
commit
debug
candidate
```

Rule đơn giản:

```text
Giá trị ảnh hưởng kết quả -> param
Giá trị dùng để phân loại/lọc/ghi chú -> tag
Giá trị đo được -> metric
File/output -> artifact
```

### 16.5. Artifact strategy

Nên log:

- Best model.
- Final model nếu cần.
- Evaluation report.
- Confusion matrix.
- Prediction sample.
- Label mapping.
- Tokenizer.
- Config file.

Không nên log:

- Toàn bộ raw data nhạy cảm.
- Checkpoint quá thường xuyên.
- File cache tạm.
- Secret.

### 16.6. Model URI strategy

Trong notebook/debug:

```text
runs:/<run_id>/model
```

Trong staging/production:

```text
models:/model-name@champion
models:/model-name@challenger
```

Không nên hard-code run id trong production API nếu đã có Registry.

## 17. Tối ưu và vận hành

### 17.1. Logging frequency

Không cần log mọi batch nếu training rất dài.

```python
if global_step % 50 == 0:
    mlflow.log_metric("train_loss", loss.item(), step=global_step)
```

Gợi ý:

| Tình huống | Cách log |
| --- | --- |
| Dataset nhỏ | Log mỗi epoch. |
| Training dài | Log mỗi N step. |
| Distributed training | Chỉ rank 0 log metric chính. |
| Debug | Log thêm artifact/sample tạm thời. |
| Production training | Log metric ổn định, artifact quan trọng. |

### 17.2. Artifact lớn

Với artifact lớn:

- Dùng MinIO/S3 thay vì local disk.
- Log best/final checkpoint thay vì mọi checkpoint.
- Nén report nếu phù hợp.
- Dọn lifecycle ở object storage.
- Không upload dữ liệu nhạy cảm chưa sanitize.

### 17.3. Backend store

Local SQLite phù hợp để học và thử nhanh. Với team hoặc production:

- Dùng PostgreSQL/MySQL.
- Backup định kỳ.
- Theo dõi dung lượng bảng metric.
- Giới hạn logging frequency.
- Có migration/upgrade plan.

### 17.4. Artifact store

Production artifact store nên:

- Bền vững.
- Có backup/lifecycle.
- Có access control.
- Có network ổn định với MLflow server và worker.
- Có naming/bucket rõ ràng.

MinIO phù hợp cho local lab hoặc self-host S3-compatible.

### 17.5. Distributed training

Trong DDP, chỉ nên cho main process log:

```python
if rank == 0:
    mlflow.log_metric("train_loss", loss_value, step=global_step)
```

Nếu mỗi process tạo run riêng, cần set tag hoặc parent/child run rõ ràng.

### 17.6. Nested runs

Nested runs hữu ích khi một experiment lớn có nhiều sub-run:

```python
with mlflow.start_run(run_name="sweep-parent"):
    for lr in [1e-2, 1e-3, 1e-4]:
        with mlflow.start_run(run_name=f"lr={lr}", nested=True):
            mlflow.log_param("learning_rate", lr)
            train_model()
```

Nested runs giúp nhóm nhiều lần thử trong một parent run.

### 17.7. Search và filter

Ví dụ search run:

```python
from mlflow import MlflowClient

client = MlflowClient()
runs = client.search_runs(
    experiment_ids=["1"],
    filter_string="metrics.val_accuracy > 0.9 and params.model_name = 'resnet18'",
    order_by=["metrics.val_accuracy DESC"],
)
```

Search tốt phụ thuộc vào việc đặt tên metric/param/tag nhất quán.

## 18. Bảo mật và dữ liệu nhạy cảm

### 18.1. Tracking server exposure

Không nên mở MLflow server public mà không cấu hình bảo mật.

Khi dùng:

```bash
mlflow server --host 0.0.0.0
```

cần chú ý:

- Auth.
- Reverse proxy.
- TLS.
- Allowed hosts.
- CORS.
- Network policy.
- Firewall.

### 18.2. Secret

Không log secret vào:

- Parameter.
- Tag.
- Artifact.
- Model metadata.
- Input example.
- Prompt.
- Trace.
- Report.

Secret gồm:

- API key.
- Database password.
- Access token.
- Private endpoint.
- Customer data.

### 18.3. Dữ liệu cá nhân

Trước khi log dataset sample hoặc prediction:

- Kiểm tra PII.
- Ẩn email/số điện thoại.
- Hash user id nếu cần.
- Chỉ log aggregate metric nếu dữ liệu nhạy cảm.
- Kiểm tra quyền project/server.

### 18.4. Pickle và model loading

Nhiều model Python dùng pickle/cloudpickle. Không load model từ nguồn không tin cậy.

Nên:

- Chỉ load model từ registry/artifact store tin cậy.
- Kiểm tra dependency.
- Dùng signature/input example.
- Review model package trước khi deploy.
- Cân nhắc Models From Code hoặc format ít phụ thuộc pickle khi phù hợp.

### 18.5. Environment variables trong model

MLflow có thể ghi nhận tên một số environment variable dùng trong inference để hỗ trợ deployment. Dù giá trị không được lưu, vẫn cần review metadata trước khi chia sẻ model vì tên biến có thể tiết lộ kiến trúc hệ thống.

## 19. Ưu điểm và hạn chế

### 19.1. Ưu điểm

- Mã nguồn mở và phổ biến.
- Dễ chạy local, không cần account để bắt đầu.
- Theo dõi experiment rõ ràng bằng UI.
- Hỗ trợ model packaging chuẩn.
- Có Model Registry cho version và alias.
- Có thể self-host với PostgreSQL và MinIO/S3.
- Tích hợp nhiều framework như scikit-learn, PyTorch, TensorFlow, XGBoost, LightGBM.
- Có autologging để bắt đầu nhanh.
- Có serving và Docker workflow.
- Có GenAI tracing/evaluation cho LLM/agent.
- Phù hợp để xây nền tảng MLOps nội bộ.

### 19.2. Hạn chế

- UI experiment tracking có thể không bóng bẩy bằng một số SaaS chuyên visualization.
- Self-host production cần hiểu backend store, artifact store, auth, backup và network.
- Nếu log quá nhiều metric/artifact, backend có thể phình lớn.
- Model Registry workflow cần quy ước rõ để tránh lộn xộn.
- Autologging không thay thế được logging thủ công cho metric nghiệp vụ.
- Serving mặc định phù hợp demo/staging; production lớn thường cần thêm platform serving riêng.
- Với LLM app phức tạp, cần hiểu rõ khác biệt giữa Tracking thường và GenAI tracing/evaluation.

## 20. Các lỗi thiết kế thường gặp

### 20.1. Không log parameter đầy đủ

Chỉ log accuracy mà không log learning rate, batch size, dataset version hoặc seed khiến run khó tái lập.

### 20.2. Log metric bằng key động

Không nên:

```python
mlflow.log_metric(f"user_{user_id}_loss", loss)
```

Nên lưu dữ liệu dạng bảng/file artifact hoặc aggregate metric.

### 20.3. Dùng local file store cho team production

File store local dễ hỏng khi nhiều máy cùng ghi hoặc khi container bị xóa. Team production nên dùng tracking server với database và artifact store bền vững.

### 20.4. Chỉ log checkpoint `.pt` mà không log MLflow Model

Checkpoint `.pt` hữu ích để resume training, nhưng khó serve trực tiếp bằng MLflow Serving. Nếu cần deploy, nên log model theo MLflow flavor hoặc pyfunc.

### 20.5. Không log signature

Không có signature, serving dễ gặp lỗi input schema. Nên dùng `infer_signature()` và `input_example`.

### 20.6. Hard-code run id trong production

Không nên:

```python
model_uri = "runs:/abc123/model"
```

Nên:

```python
model_uri = "models:/iris-classifier@champion"
```

### 20.7. Upload artifact quá nhiều

Log checkpoint mỗi batch có thể làm artifact store tăng rất nhanh. Nên log best/final hoặc theo chu kỳ hợp lý.

### 20.8. Không kiểm soát secret

Không log API key, password, private prompt hoặc dữ liệu khách hàng vào param/tag/artifact/trace.

### 20.9. Không backup backend store

Artifact còn nhưng metadata mất thì lineage và registry cũng mất. Cần backup database MLflow.

### 20.10. Không tách experiment

Gom mọi run vào một experiment lớn làm UI khó dùng. Nên tách theo bài toán, dataset hoặc service.

### 20.11. Lạm dụng autologging

Autologging tiện nhưng có thể log nhiều thứ không mong muốn hoặc thiếu metric nghiệp vụ. Nên review output và bổ sung logging thủ công.

### 20.12. Mở tracking server ra mạng mà không cấu hình bảo mật

MLflow server chứa metric, artifact, model và có thể chứa dữ liệu nhạy cảm. Cần auth, TLS, network policy và allowed hosts.

## 21. Bài tập thực hành

### Bài 1: Cài và chạy MLflow UI

Cài:

```bash
pip install mlflow
```

Chạy:

```bash
mlflow server --port 5000
```

Mở:

```text
http://127.0.0.1:5000
```

### Bài 2: Log run cơ bản

Viết script log:

- `learning_rate`
- `batch_size`
- `train_loss`
- `val_accuracy`
- tag `stage=debug`

Kiểm tra run trong MLflow UI.

### Bài 3: Train scikit-learn model

Train Logistic Regression trên Iris dataset. Log:

- Params.
- Accuracy.
- F1 macro.
- Model bằng `mlflow.sklearn.log_model()`.
- Signature và input example.

### Bài 4: Load model inference

Load model từ:

```text
runs:/<run_id>/model
```

Dùng `mlflow.pyfunc.load_model()` để predict trên test set.

### Bài 5: Log artifact

Tạo file `classification_report.txt` hoặc `predictions.csv` và log vào artifact path `reports`.

### Bài 6: Model Registry

Register model tên `iris-classifier`, tạo alias:

```text
champion
```

Load model bằng:

```text
models:/iris-classifier@champion
```

### Bài 7: Serve model

Serve model:

```bash
mlflow models serve -m "models:/iris-classifier@champion" -p 5000
```

Gọi `/invocations` bằng `curl` hoặc Python `requests`.

### Bài 8: MLflow + PyTorch

Train một MLP nhỏ bằng PyTorch. Log:

- Params.
- Train loss theo epoch.
- Train accuracy theo epoch.
- Best checkpoint artifact.
- Model bằng `mlflow.pytorch.log_model()`.

### Bài 9: MLflow + MinIO

Chạy MLflow server với:

- PostgreSQL backend store.
- MinIO artifact store.

Log một artifact và kiểm tra object trong MinIO Console.

### Bài 10: RAG evaluation

Dựa trên các file trong `docs`, thiết kế run evaluation cho RAG:

- Log chunking config bằng params.
- Log retrieval/answer metrics.
- Log output JSON hoặc CSV bằng artifact.
- Log vector database đang dùng bằng tag hoặc param.

## 22. Lộ trình học đề xuất

1. Hiểu experiment, run, parameter, metric, tag và artifact.
2. Cài MLflow và chạy UI local.
3. Log run thủ công bằng `start_run`, `log_param`, `log_metric`, `log_artifact`.
4. Train scikit-learn model và log bằng `mlflow.sklearn.log_model`.
5. Load model bằng `mlflow.pyfunc.load_model`.
6. Học model signature và input example.
7. Tích hợp MLflow vào PyTorch training loop.
8. Dùng autologging và hiểu khi nào nên log thủ công.
9. Chạy Tracking Server cho team.
10. Cấu hình PostgreSQL backend store.
11. Cấu hình MinIO/S3 artifact store.
12. Dùng Model Registry, version và alias.
13. Serve model bằng `mlflow models serve`.
14. Thiết kế CI/CD promotion với `champion` và `challenger`.
15. Học MLflow Evaluation cho classification/regression.
16. Nếu làm RAG/LLM, học MLflow GenAI tracing và evaluation.

## 23. Kết luận

MLflow là một nền tảng quan trọng trong MLOps vì nó giúp quản lý toàn bộ vòng đời model: từ thí nghiệm, log metric, lưu artifact, đóng gói model, đăng ký version, đánh giá, cho đến serving. Thay vì để model nằm rải rác dưới dạng file checkpoint không rõ nguồn gốc, MLflow gắn model với run, parameter, metric, dataset, dependency và registry metadata.

Về mặt kỹ thuật, MLflow xoay quanh các khái niệm experiment, run, parameter, metric, tag, artifact, MLflow Model, flavor, signature, Model Registry và Tracking Server. Khi self-host, cần hiểu rõ backend store và artifact store: metadata nên nằm trong database như PostgreSQL, còn file lớn nên nằm trong object storage như MinIO/S3.

Trong repo này, MLflow đặc biệt phù hợp để bổ sung cho PyTorch training, RAG evaluation, vector database benchmark, FastAPI worker và Docker-based infrastructure. PostgreSQL có thể làm backend store, MinIO có thể làm artifact store, FastAPI có thể tạo job hoặc wrap inference, còn LangChain/LangGraph có thể kết hợp với MLflow Tracking hoặc GenAI tracing để đánh giá workflow LLM/RAG.

Khi dùng MLflow trong dự án thật, cần thiết kế logging có chủ đích: đặt tên experiment/run rõ ràng, log params đầy đủ, log metric ổn định, dùng artifact đúng chỗ, log model có signature, quản lý registry bằng alias và bảo vệ dữ liệu nhạy cảm. MLflow không tự làm thí nghiệm trở nên tốt hơn, nhưng nó giúp mọi quyết định trong quá trình phát triển model được ghi lại và truy vết rõ ràng.

## 24. Tài liệu tham khảo

- MLflow Documentation: https://mlflow.org/docs/latest/
- MLflow for Machine Learning: https://mlflow.org/docs/latest/ml/
- MLflow Tracking Quickstart: https://mlflow.org/docs/latest/ml/tracking/quickstart/
- MLflow Tracking Server: https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/
- MLflow Autologging: https://mlflow.org/docs/latest/ml/tracking/autolog/
- MLflow System Metrics: https://mlflow.org/docs/latest/ml/tracking/system-metrics/
- MLflow Models: https://mlflow.org/docs/latest/ml/model/
- MLflow Model Signatures: https://mlflow.org/docs/latest/ml/model/signatures/
- MLflow Model Registry: https://mlflow.org/docs/latest/ml/model-registry/
- MLflow Model Serving: https://mlflow.org/docs/latest/ml/deployment/
- Deploy MLflow Model Locally: https://mlflow.org/docs/latest/ml/deployment/deploy-model-locally/
- MLflow Docker Image: https://mlflow.org/docs/latest/ml/docker/
- MLflow Model Evaluation: https://mlflow.org/docs/latest/ml/evaluation/
- MLflow for LLMs and Agents: https://mlflow.org/docs/latest/genai/
- MLflow API Reference: https://mlflow.org/docs/latest/api_reference/
- MLflow Self-Hosting: https://mlflow.org/docs/latest/self-hosting/
