# AppRunnerが対応しているPlatformを明示的に指定する
FROM --platform=linux/x86_64 python:3.11.3

WORKDIR /app

COPY . /app

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetryをダウンロードしてインストール
RUN curl -sSL https://install.python-poetry.org | python -

# Pathを通す
ENV PATH /root/.local/bin:$PATH
# 仮想環境をたてない
RUN poetry config virtualenvs.create false

## アプリケーションの依存関係をインストール
RUN poetry install

EXPOSE 7860

CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
