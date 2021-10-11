# GPT-3 example
from transformers import AutoTokenizer, AutoModelWithLMHead
from multiprocessing import Pool
from transformers import pipeline, set_seed
from pprint import pprint


def do(text):
	print("doing: ", text)
	generator = pipeline('text-generation', model='sberbank-ai/rugpt3large_based_on_gpt2')
	set_seed(42)
	# x = generator("Грозный Генька генератор грубо грыз горох горстями,", max_length=130, num_return_sequences=1)
	x = generator(text,  # max_length=30, num_return_sequences=2,
				  max_length=30,
				  # min_length=30,
				  length_penalty=5,
				  num_beams=4,
				  num_return_sequences=2,
				  early_stopping=True
				  )
	return x

if __name__ == '__main__':
	# ----------GPT-3--------------		
	chunksize = 1
	dataset = ['Грозный Генька-генератор грубо грыз горох горстями,',
			   'Нам нужна одна победа,',
			   'Давайте говорить друг другу комплименты,',
			   ]
	with Pool(processes=10) as pool:
		result = pool.map(do, dataset, chunksize)		
	pprint(result)

# Грозный Генька генератор грубо грыз горох горстями,
# а я, как всегда, сидел на корточках и смотрел на него


----------------



import torch
from transformers import AutoTokenizer, AutoModel, AutoModelWithLMHead, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForMaskedLM
tokenizer = AutoTokenizer.from_pretrained(«artemsnegirev/ru_gpt3_large»)
#AutoModelForCausalLM AutoModelForSeq2SeqLM AutoModelForMaskedLM
model = AutoModelForCausalLM.from_pretrained(«artemsnegirev/ru_gpt3_large»)
model.eval()
model.to('cuda')

def generate(text):
# encode context the generation is conditioned on
input_ids = tokenizer.encode(text, return_tensors='pt')
input_ids = input_ids.to('cuda')
# generate text until the output length (which includes the context length) reaches 50
greedy_output = model.generate(input_ids, max_length=100)
return tokenizer.decode(greedy_output[0], skip_special_tokens=True)

generate(«Маньяк читает книгу про глубокое обучение»)

--------------

Вот с таким черновиком Dockerfile запускаю ruGPT2048

FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime
USER root

# installing full CUDA toolkit
RUN apt update
RUN pip install --upgrade pip
RUN apt install -y build-essential g++ llvm-8-dev git cmake wget
RUN conda install -y -c conda-forge cudatoolkit-dev
# setting environment variables
ENV CUDA_HOME "/opt/conda/pkgs/cuda-toolkit"
ENV CUDA_TOOLKIT_ROOT_DIR $CUDA_HOME
ENV LIBRARY_PATH "$CUDA_HOME/lib64:$LIBRARY_PATH"
ENV LD_LIBRARY_PATH "$CUDA_HOME/lib64:$CUDA_HOME/extras/CUPTI/lib64:$LD_LIBRARY_PATH"
ENV CFLAGS "-I$CUDA_HOME/include $CFLAGS"
# installing triton
WORKDIR /workspace
RUN apt install -y llvm-9-dev
RUN pip install triton==0.2.1
RUN pip install torch-blocksparse
ENV PYTHONPATH "${PYTHONPATH}:/workspace/src/triton/python:/workspace/torch-blocksparse"

RUN git clone https://github.com/NVIDIA/apex && cd apex && pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./
COPY requirements.txt /tmp/requirements.txt # requirements из репы с ru-gpts
RUN pip install -r /tmp/requirements.txt
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]

------

Запустил все модели на 2070Super. С ruGPT2048 намучался больше всего. На CUDA 10.1 остановился на следующем:

Сначала по инструкции

python -m pip install virtualenv
virtualenv gpt_env
source gpt_env/bin/activate
pip install -r requirements.txt

Затем возникли проблемы с torch/apex/torch-blocksparse которых в requirements.txt нет. С этими версиями работает:

pip install torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f download.pytorch.org/whl/torch_stable.html

sudo apt install llvm-9

git clone github.com/NVIDIA/apex #8a1ed9e
cd apex
pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext".

pip install torch-blocksparse #1.1.1

В таком порядке. Затем в scripts/generate_ruGPT2048.sh заменить load и tokenizer-path на путь к распакованной модели (rugpt2048.tar.gz )

Затем запустить scripts/generate_ruGPT2048.sh