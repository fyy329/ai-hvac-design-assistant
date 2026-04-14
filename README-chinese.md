# AI 暖通空调设计助手

基于 AI 的暖通空调系统设计、负荷计算与仿真自动化工具包。

[![CI](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml)
[![Lint](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml/badge.svg)](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml)
[![License](https://img.shields.io/github/license/fyy329/ai-hvac-design-assistant)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

## 功能概述

该项目聚焦于暖通空调工程设计初期的常见工作流程：

- 确定性供暖负荷计算
- 基于规则和 AI 辅助的系统推荐
- 面向 Polysun 的仿真模板
- Modelica 骨架代码生成
- 单位换算与输入校验辅助工具

目标是在不隐藏工程假设的前提下，让重复性的设计和仿真配置工作更易于自动化。

## 安装

```bash
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant
python -m venv .venv

## 激活虚拟环境
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

## 安装包及开发工具：
pip install -e ".[dev]"

## 如需使用 AI 相关功能，请创建 .env 文件并添加你的 API 密钥：
cp .env.example .env

Copy-Item .env.example .env

##然后设置
OPENAI_API_KEY=sk-your-key-here

# 快速入门
## Python API
from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator

calc = HeatingLoadCalculator(
    climate_zone=ClimateZone.MODERATE_COLD,
    building_type="residential",
    heated_area_m2=450,
)

envelope = EnvelopeSpec(
    wall_area_m2=300,
    roof_area_m2=150,
    floor_area_m2=150,
    window_area_m2=60,
)

result = calc.calculate(envelope)

print(f"Heating load: {result.total_heating_load_kw:.1f} kW")
print(f"Specific load: {result.specific_load_w_per_m2:.0f} W/m2")

## AI辅助系统推荐
for component in recommendation.components:
    print(f"  - {component}")
from ai_hvac import HVACAssistant

assistant = HVACAssistant()
recommendation = assistant.recommend_system(
    building_type="multi-family residential",
    location="Munich, Germany",
    heated_area_m2=2400,
    additional_context="Underfloor heating, 35/28 degC design temps, rooftop PVT possible",
)

print(recommendation.system_type)
print(recommendation.estimated_cop)
for component in recommendation.components:
    print(f"  - {component}")

## Polysun 模板生成：

python
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

generator = PolysunTemplateGenerator(heating_load_kw=25.0, dhw_demand_litres_day=400)
template = generator.heat_pump_template(hp_type="ground_source", with_solar=True)
print(template.to_json())
CLI
## 本包提供 ai-hvac 命令：

bash
ai-hvac version
从命令行进行供暖负荷计算：

bash
ai-hvac load-calc --heated-area-m2 480 --wall-area-m2 320 --roof-area-m2 160 --floor-area-m2 160 --window-area-m2 70
输出面向 Polysun 的模板：

bash
ai-hvac polysun-template --heating-load-kw 25 --with-solar

开发
在推送前，请在本地运行核心检查：

bash
pytest
ruff check src tests examples
ruff format --check src tests examples
mypy src tests examples
basedpyright
示例脚本：

bash
python examples/basic_load_calculation.py
python examples/polysun_template_generation.py
python examples/ai_system_recommendation.py
AI 示例需要 OPENAI_API_KEY。

项目结构
text
src/ai_hvac/
|- core/        # 配置和异常类型
|- hvac/        # 负荷计算、系统设计、参考数据
|- llm/         # OpenAI 客户端、提示词、解析辅助
|- simulation/  # Polysun 和 Modelica 模板生成
`- utils/       # 转换器和校验器
 文档
入门指南

架构说明

API 参考

路线图

支持的标准与工具标准 / 工具	覆盖范围
DIN EN 12831	简化供暖负荷计算
DIN 4108 / EnEV / GEG	参考 U 值表
DIN 4708 / VDI 2067	生活热水需求曲线
Polysun	仿真模板生成
Modelica / AixLib	骨架模型生成
ASHRAE	设计条件参考数据
贡献：欢迎贡献。详见 .github/CONTRIBUTING.md。

仍有较大改进空间的领域：

制冷负荷计算

天气与气候文件集成

自动化 Polysun 导出格式

暖通空调标准检索 / RAG

网页界面与可视化

许可证
MIT

text
