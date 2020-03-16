# Задание №1

В этом задание предлагается познакомиться с базовой функциональностью Python. Запустите `Jupyter Notebook` или `Jupyter Lab` и следуйте инструкциям в `assignment_1.ipynb`.

## Установка и запуск jupyter

1. Скачайте и установите необходимую версию [miniconda](https://docs.conda.io/en/latest/miniconda.html)

(дальнейшая установка подразумевает работу в bash)

2. Создайте новой окружение

```bash
conda create -n assignment_1 python=3.7
```

3. Активируйте окружение

```bash
conda activate assignment_1
```

4. Установите необходимые пакеты

```bash
conda install numpy matplotlib
```

5. Установите `jupyter`

```bash
conda install -c conda-forge jupyterlab
```

или

```bash
conda install -c conda-forge notebook
```

6. Запустите `jupyter`

```bash
jupyter lab
```

или

```bash
jupyter notebook
```
