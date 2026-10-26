# Part of the custom module partner_validations.
import re

from odoo import api, models, _
from odoo.exceptions import ValidationError

# Validación pragmática de email (subconjunto ASCII de RFC 5322):
#  - parte local: letras, números y  . ! # $ % & ' * + - / = ? ^ _ ` { | } ~  (sin espacios ni acentos)
#  - exactamente un @
#  - dominio: etiquetas alfanuméricas/guiones separadas por puntos
#  - extensión final de al menos 2 letras (permite gmail.com y gmail.com.mx)
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
    r"\.[A-Za-z]{2,}$"
)

# Teléfono mexicano (estándar IFT): exactamente 10 dígitos ASCII, solo se toleran espacios al teclear.
PHONE_RE = re.compile(r"[0-9]{10}")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ------------------------------------------------------------------
    # Helpers de validación (compartidos por onchange y constrains)
    # ------------------------------------------------------------------
    @staticmethod
    def _pv_is_email_valid(email):
        return bool(EMAIL_RE.fullmatch(email.strip()))

    @staticmethod
    def _pv_is_phone_valid(phone):
        # Solo se toleran espacios como separador visual; cualquier otro
        # carácter no numérico (guiones, letras, símbolos) invalida el número.
        digits = phone.replace(" ", "")
        return bool(PHONE_RE.fullmatch(digits))

    @staticmethod
    def _pv_normalize_phone(phone):
        # Quita los espacios para persistir el teléfono limpio. Deja intacto
        # cualquier valor vacío/falsy. No elimina otros símbolos: un número
        # con guiones o letras seguirá fallando en la validación.
        if not phone:
            return phone
        return phone.replace(" ", "")

    # ------------------------------------------------------------------
    # Normalización al guardar — "flexible al aceptar, estricto al guardar"
    # Cubre todos los orígenes (UI, importación, API, código) desde el ORM.
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('phone'):
                vals['phone'] = self._pv_normalize_phone(vals['phone'])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('phone'):
            vals['phone'] = self._pv_normalize_phone(vals['phone'])
        return super().write(vals)

    # ------------------------------------------------------------------
    # Advertencias tempranas (al editar) — no bloquean, solo avisan
    # ------------------------------------------------------------------
    @api.onchange('phone')
    def _onchange_phone_normalize(self):
        # Limpia los espacios en vivo para que el usuario vea el valor
        # normalizado mientras edita (la persistencia la garantizan create/write).
        if self.phone:
            self.phone = self._pv_normalize_phone(self.phone)

    @api.onchange('email')
    def _onchange_email_warn(self):
        if self.email and not self._pv_is_email_valid(self.email):
            return {'warning': {
                'title': _("Correo electrónico inválido"),
                'message': _(
                    "El correo '%(email)s' no tiene un formato válido. "
                    "Debe ser del tipo usuario@dominio.extension.",
                    email=self.email,
                ),
            }}

    @api.onchange('phone')
    def _onchange_phone_warn(self):
        if self.phone and not self._pv_is_phone_valid(self.phone):
            return {'warning': {
                'title': _("Teléfono inválido"),
                'message': _(
                    "El teléfono '%(phone)s' no es válido. Debe contener 10 números "
                    "(los espacios se permiten y se eliminan al guardar).",
                    phone=self.phone,
                ),
            }}

    # ------------------------------------------------------------------
    # Validación final al guardar (bloquea) — se mantiene
    # ------------------------------------------------------------------
    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and not self._pv_is_email_valid(record.email):
                raise ValidationError(_(
                    "El correo electrónico '%(email)s' no tiene un formato válido. "
                    "Debe ser del tipo usuario@dominio.extension.",
                    email=record.email,
                ))

    @api.constrains('phone')
    def _check_phone_format(self):
        for record in self:
            if record.phone and not self._pv_is_phone_valid(record.phone):
                raise ValidationError(_(
                    "El teléfono '%(phone)s' no es válido. Debe contener 10 números "
                    "(los espacios se permiten y se eliminan al guardar).",
                    phone=record.phone,
                ))

