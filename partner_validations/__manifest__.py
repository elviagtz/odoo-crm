# Part of the custom module partner_validations.
{
    'name': 'Partner Validations',
    'version': '1.0',
    'category': 'Contacts',
    'summary': 'Validaciones de datos para contactos (email y teléfono).',
    'description': """
Validaciones de datos para res.partner
=======================================

Agrega validaciones a nivel de servidor sobre el modelo de contactos (res.partner):

* Email: valida que el formato sea usuario@dominio.extension.
* Teléfono: valida que tenga exactamente 10 dígitos (normaliza espacios al guardar).

La validación del número de identificación fiscal (vat / RFC) la provee el
módulo base_vat de forma nativa, según el país del contacto (México con
check_vat_mx y el resto de países con sus propias reglas). Por eso base_vat
se mantiene en 'depends'.

Las validaciones aplican en todos los módulos que comparten res.partner
(Contactos, CRM, Ventas, Facturación).
""",
    'author': 'Elvia Gutierrez',
    'license': 'LGPL-3',
    'depends': ['base', 'base_vat'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
