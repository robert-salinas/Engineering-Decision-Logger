from typing import Dict, Any
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
    """
    Formats decision data into an Architecture Decision Record (ADR) Markdown file.
    """
    def __init__(self, template_str: str = ADR_TEMPLATE):
        """
        Initializes the ADRFormatter with a Jinja2 template.

        Args:
            template_str (str): The Jinja2 template string. Defaults to ADR_TEMPLATE.
        """
        self.template = Template(template_str)

    def render(self, data: Dict[str, Any]) -> str:
        """
        Renders the decision data into a Markdown string.

        Args:
            data (Dict[str, Any]): The decision data.

        Returns:
            str: The rendered Markdown content.
        """
        if "date" not in data:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
        return self.template.render(**data)

    @staticmethod
    def get_filename(adr_id: int, title: str) -> str:
        """
        Generates a standard filename for an ADR.

        Args:
            adr_id (int): The ID of the ADR.
            title (str): The title of the decision.

        Returns:
            str: The generated filename (e.g., "0001-use-sqlmodel.md").
        """
        return f"{adr_id:04d}-{slugify(title)}.md"
