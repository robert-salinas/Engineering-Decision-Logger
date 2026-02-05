from jinja2 import Template
from datetime import datetime
from slugify import slugify

ADR_TEMPLATE = """# {{ id }}-{{ title }}

* Status: {{ status }}
* Date: {{ date }}

## Context and Problem Statement

{{ context }}

## Decision Drivers

{% for driver in drivers %}
* {{ driver }}
{% endfor %}

## Considered Options

{% for option in options %}
* {{ option }}
{% endfor %}

## Decision Outcome

Chosen option: "{{ chosen_option }}", because {{ rationale }}

### Consequences

* Good: {{ consequences_good }}
* Bad: {{ consequences_bad }}

## Pros and Cons of the Options

{% for option in pros_cons %}
### {{ option.name }}

* Good, because {{ option.pros }}
* Bad, because {{ option.cons }}
{% endfor %}
"""

class ADRFormatter:
    def __init__(self, template_str: str = ADR_TEMPLATE):
        self.template = Template(template_str)

    def render(self, data: dict) -> str:
        if "date" not in data:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
        return self.template.render(**data)

    @staticmethod
    def get_filename(adr_id: int, title: str) -> str:
        return f"{adr_id:04d}-{slugify(title)}.md"
