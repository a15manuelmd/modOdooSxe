# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Games(models.Model):
    _name = 'games'
    _description = 'games'

    name = fields.Char('Titulo', required=True)
    description = fields.Text('Descripción')
    videoUrl = fields.Char('Video Url')
    price = fields.Float('Precio', default=59.99)
    date_release = fields.Date('Fecha de Lanzamiento', default = lambda *a:datetime.now().strftime('%Y-%m-%d'))
    author_ids = fields.Many2many('res.partner', string = 'Desarrolladora')
    category_id = fields.Many2many('games.category', string = 'Géneros')
    image = fields.Binary('Portada')
    state = fields.Selection([
        ('unavailable', 'No Disponible'),
        ('available', 'Disponible')],
        'State', default = "unavailable")

    reserve_ids = fields.One2many('game.reserve', inverse_name = 'game_id')

#cambia el estado, si es el mismo, no hace nada
    @api.multi
    def change_state(self, new_state):
        for game in self:
            if game.state == new_state:
                mensage = ('Ya estaba como: %s!!!',new_state)
                raise models.ValidationError(mensage)
                return
            else:
                game.state = new_state
                return

    def make_available(self):
        self.change_state('available')

    def make_unavailable(self):
        self.change_state('unavailable')

#se encarga de realizar un pedido, se ejecuta con privilegios, para que lo pueda ejecutar un usuario normal, sin tener que darle permisos especiales.
    def reserve(self):
        partner = self.env['res.users'].browse(self.env.uid).partner_id
        clients = self.env['game.client']
        idCli = 0
        for client in clients.search([]):
            if (client.partner_id.id == partner.id):
                idCli=client.id
        if idCli == 0:
            raise models.ValidationError("Este usuario tiene que ser agregado como cliente para poder hacer reservas")
            return
        for rec in self:
          inv_obj = self.env['game.reserve']
          self.ensure_one()
          invoice = inv_obj.sudo().create({
          'client_id': idCli,
              'game_id': self.id
          })
          return invoice
