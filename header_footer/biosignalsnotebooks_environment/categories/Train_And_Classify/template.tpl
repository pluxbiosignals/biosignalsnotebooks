
{% extends 'full.tpl'%}
{% block any_cell %}
{% if 'hide_in' in cell['metadata'].get('tags', []) %}
    <div class="hide_in">
        {{ super() }}
    </div>
{% elif 'hide_out' in cell['metadata'].get('tags', []) %}
    <div class="hide_out">
        {{ super() }}
    </div>
{% elif 'hide_both' in cell['metadata'].get('tags', []) %}
    <div class="hide_both">
        {{ super() }}
    </div>
{% elif 'hide_mark' in cell['metadata'].get('tags', []) %}
    <div class="hide_mark">
        {{ super() }}
    </div>
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}