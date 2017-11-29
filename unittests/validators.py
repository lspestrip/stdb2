# -*- encoding: utf-8 -*-

VALID_REPORT_EXTENSIONS = [
    '.pdf',
    '.doc',
    '.docx',
    '.html',
    '.htm',
    '.xsl',
    '.xslx',
    '.md',
    '.rst',
]


def validate_report_file_ext(value):
    import os

    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in VALID_REPORT_EXTENSIONS:
        raise ValidationError('unsupported file extension "{0}", valid extensions are {1}'
                              .format(ext, ', '.join(['"' + x + '"' for x in VALID_REPORT_EXTENSIONS])))
