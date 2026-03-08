本仓库的目的是：测评和比较各种自部署小模型的翻译效果

我的电脑配置如下：

- CPU: Intel Core i7-14650H
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU(8GB)
- 内存: 32GB
- 操作系统: Windows 11
- Python版本: 3.14

# 评测方法

1. **评测指标**：根据BLEU、CHRF指标来评测翻译质量
2. **主观评测**：有我个人主观的评测标准。
3. **外部LLM打分**：使用外部的LLM来对翻译结果进行打分

## BLEU指标

> Bilingual Evaluation Understudy. 一种自动化的评测机器翻译质量的方法，通过比较机器翻译的输出和一个或多个参考翻译来计算得分。BLEU得分越高，表示机器翻译的质量越好。

## CHRF指标

> chrF 是一种自动评估指标，通过比较字符序列而不是完整单词，来评估候选文本（例如，机器翻译的输出）与一个或多个参考文本之间的相似度. 它计算了候选文本和参考文本之间的字符n-gram的精确度和召回率，并将它们结合成一个综合得分。chrF得分越高，表示候选文本与参考文本之间的相似度越高。


# 环境安装

```
uv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

执行完上述命令后，环境就搭建好了。

# 程序主入口

程序主入口在`run_eval.py`文件中，运行该文件即可开始评测。如果模型文件不存在，第一次运行的时候会自动下载模型。默认运行的是全部模型的评测，如果只想评测某个模型，可以使用以下命令：

```
python run_eval.py --model MODEL_NAME
```

另外还有其他的命令行参数可以使用，具体可以使用以下命令来查看：

```
python run_eval.py --help
```

# 如何添加新的模型？

在`config/models.yaml`文件中添加新的模型配置，然后在`translators`文件夹中实现对应的翻译器类。完成后就可以在评测中使用新的模型了。

对应的翻译类可以继承`BaseTranslator`类，并实现其中的两个方法(理论上来讲只需要实现两个，并且都是大同小异)。具体可以参考`translators/smolLM3.py`文件中的`SmolLMTranslator`类的实现。

实现完成后可以使用以下命令来运行评测：

```
python run_eval.py --model MODEL_NAME
```

其中`MODEL_NAME`是你想要评测的模型名称，必须与`config/models.yaml`中的配置一致。

另外，`config/models.yaml` 中的model_name 必须要和HuggingFace上模型的名称一致，否则程序会无法下载模型文件。

# 测试数据

测试数据保存在`data`文件夹中，格式为JSON。

```
{
    "source": "发布以上内容，发布者自行承担法律责任、道德风险，且最高可永久封禁社区账号。",
    "reference": "By posting the above content, the publisher assumes legal responsibility and moral risk, and may be permanently banned from the community account at most.",
    "src_lang": "zh",
    "tgt_lang": "en"
},
```

以上为一个测试数据的示例，包含了源语言文本、参考翻译文本、源语言和目标语言的信息。

src_lang和tgt_lang的值可以在`utils/lang_codes.py`文件中找到

# 外部LLM打分

如果启用了外部LLM打分功能，需要格外的配置API_KEY。配置示例请看`.env.example`文件。

也可以使用中转站的来进行API调用，修改`config/scoring.yaml`文件中的配置即可。

```
scoring:
  deepseek:
    enabled: false
    model: deepseek-translate-eval-20250514
    api_base: https://api.deepseek.com/v1
    # API key from env: DEEPSEEK_API_KEY
```

以上为配置示例，启用某个模型的打分功能需要将对应的`enabled`字段设置为`true`，并且配置好API_KEY。

# 评测结果

评测的结果会保存在`results`文件夹中，每个模型的评测结果会保存在一个单独的文件中。

评测结果的格式为JSON，包含了每个测试数据的源文本、参考翻译、模型翻译结果、BLEU得分、CHRF得分以及外部LLM打分（如果启用了的话）。

```
{
      "source": "我非常感激佬友们对 LINUX DO 的喜爱与支持，也非常明白你们希望加入讨论的迫切心情。但所谓欲速则不达，我还是恳求希望加入的佬友们能看一看这个帖子再做账号申请，以增加成功率和申请效率。",
      "reference": "I am very grateful for the love and support of the users for LINUX DO, and I understand your eagerness to join the discussion. However, as the saying goes, \"Haste makes waste,\" I sincerely request that those who wish to join take a look at this post before applying for an account, to increase the success rate and efficiency of the application.",
      "translation": "I am very grateful for your love and support of LINUX DO, and I fully understand your urgent desire to join in the discussion. But haste makes waste, so I still kindly request that those who wish to join look at this post before applying for an account, in order to increase both success rate and application efficiency.",
      "src_lang": "zh",
      "tgt_lang": "en",
      "bleu": 41.01,
      "chrf": 68.33,
      "time_seconds": 2.398
    }
```

其中`source`为源文本，`reference`为参考翻译(Google translate)，`translation`为模型翻译结果，`src_lang`和`tgt_lang`分别为源语言和目标语言，`bleu`和`chrf`分别为BLEU得分和CHRF得分，`time_seconds`为模型翻译所花费的时间（单位为秒）。

