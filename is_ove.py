# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging
import os
import re
import hashlib
from openerp import tools
from openerp.exceptions import AccessError


_logger = logging.getLogger(__name__)


    
class is_gender(osv.osv):
    _name = 'is.gender'
    _description = 'Sexe'
    
    _columns = {
        'name': fields.char('Sexe', required=True),
    }
    
is_gender()
   
    
class is_usager(osv.osv):
    _name = 'is.usager'
    _description = 'Usager'
    
    _columns = {
        'name': fields.char('Nom', required=True),
        'usager_name_jf': fields.char('Nom de jeune fille'),
        'usager_first_name': fields.char(u'Prénom', required=True),
        'usager_birthday': fields.date('Date de naissance'),
        'usager_birth_place': fields.char('Lieu de naissance'),
        'usager_gender_id': fields.many2one('is.gender', 'Sexe', required=True),
        }

is_usager()

class is_dossier_usager(osv.osv):
    _name = 'is.dossier.usager'
    _description = 'Dossier usager'
    _rec_name = 'usager_id'
    
    _columns = {
        'usager_id': fields.many2one('is.usager', 'Usager', required=True),
        
        'image': fields.binary("Image"),   
        'coor_father_id': fields.many2one('is.usager.parent', u'Père'),
        'coor_mother_id': fields.many2one('is.usager.parent', u'Mère'),
        'coor_association_id': fields.many2one('is.usager.parent', 'Association titulaire'),
        'coor_start_date': fields.date(u"Date d'entrée dans la structure"),
        'coor_nationality': fields.char(u'Nationalité'),
        'coor_ident_compta': fields.char('Identifiant Compta'),
        
        'adr_type_hebergement': fields.many2one('is.type.hebergement', u'Type hébergement'),
        'adr_chez': fields.char('Chez'),
        'adr_street': fields.char('Rue'),
        'adr_lieu_dit': fields.char('Lieu dit'),
        'adr_zip': fields.char('Code postal', size=24),
        'adr_city': fields.char('Ville'),
        'adr_phone_ids': fields.one2many('is.phone', 'usager_id', u'Téléphone(s)'),
        'adr_email_ids': fields.one2many('is.email', 'usager_id', u'Courriel(s)'),        
        'adr_autre_adresse_ids': fields.one2many('is.autre.adresse', 'usager_id', u'Autre adresse / Personne à contacter'),
        
        'sf_responsable_id': fields.many2one('is.responsable.legal', u'Responsable légal'),
        'sf_situation_parent_id': fields.many2one('is.situation', 'Situation des parents'),
        'sf_rang': fields.char('Rang dans la fratrie'),
        'sf_nb_sisters': fields.integer(u'Nombre des soeurs'),
        'sf_nb_brothers': fields.integer(u'Nombre des frères'),
        'sf_situation_usager_id': fields.many2one('is.situation', "Situation de l'usager"),
        'sf_nb_children': fields.integer("Nombre d'enfants"),
        'sf_nb_children_charge': fields.integer(u"Nombre d'enfants à charge"), 
        
        'notification_ids': fields.one2many('is.usager.notification', 'usager_id', 'Notifications'),
        'affiliation_ids': fields.one2many('is.usager.affiliation', 'usager_id', 'Affiliations'),
        'prestation_ids': fields.one2many('is.usager.prestation', 'usager_id', 'Prestations'),
        'autorisation_ids': fields.one2many('is.usager.autorisation', 'usager_id', 'Autorisations'),
        'contre_indication_ids': fields.one2many('is.usager.contre.indications', 'usager_id', 'Contre-indications'),
        'soins_ids': fields.one2many('is.usager.soins', 'usager_id', 'Soins'),
        
        'group_consultation': fields.many2one('ove.groupe', u'Accès à la consultation', readonly=True),
        'group_modification': fields.many2one('ove.groupe', u'Accès à la modification', readonly=True),
    }
    
    def onchange_usager_id(self, cr, uid, ids, usager_id, context=None):
        val = {}
        if usager_id:
            group_obj = self.pool.get('ove.groupe')
            group_ids = group_obj.search(cr, uid, [('usager_id','=', usager_id)], context=context)
            if group_ids:
                for group in group_obj.read(cr, uid, group_ids, ['id', 'code', 'user_ids'], context=context):
                    if group['code'] == 'G2':
                        val.update({'group_consultation': group['id']}) 
                    if group['code'] == 'G3':
                        val.update({'group_modification': group['id']})    
        return {'value': val}
    
    def create(self, cr, uid, vals, context=None):
        """
        Prendre en considération les groupes d'accéssibilité lors de la création
        """
        new_id = super(is_dossier_usager, self).create(cr, uid, vals, context=context)
        val = self.onchange_usager_id(cr, uid, [new_id], vals['usager_id'], context)
        self.write(cr, uid, new_id, val['value'], context=context)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        """
        Prendre en considération les groupes d'accessibilité lors de la modification
        """
        if 'usager_id' in vals and vals['usager_id']:
            val = self.onchange_usager_id(cr, uid, ids, vals['usager_id'], context)
            vals.update(val['value'])
        return super(is_dossier_usager, self).write(cr, uid, ids, vals, context=context)

is_dossier_usager()

class is_type_parent(osv.osv):
    _name = 'is.type.parent'
    _description = 'Types parents'
    
    _columns = {
        'name': fields.char('Type'),
    }
    
is_type_parent()

class is_phone(osv.osv):
    _name = 'is.phone'
    _description = u'Téléphones des usagers'
    
    _columns = {
        'name': fields.char('Nom'),
        'phone': fields.char(u'Téléphone'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_phone()

class is_email(osv.osv):
    _name = 'is.email'
    _description = u'Courriels des usagers'
    
    _columns = {
        'name': fields.char('Nom'),
        'email': fields.char('Courriel'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_email()

class is_autre_adresse(osv.osv):
    _name = 'is.autre.adresse'
    _description = 'Autres adresses des usagers'
    
    _columns = {
        'name': fields.char('Nom'),
        'aa_first_name': fields.char(u'Prénom'),
        'aa_lieu': fields.char("Lieu avec l'usager"),
        'aa_street': fields.char('Rue'),
        'aa_lieu_dit': fields.char('Lieu dit'),
        'aa_zip': fields.char('Code postal', size=24),
        'aa_city': fields.char('Ville'),
        'aa_phone': fields.char(u'Téléphone(s)'),
        'aa_email': fields.char('Courriel(s)'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_autre_adresse()


class is_responsable_legal(osv.osv):
    _name = 'is.responsable.legal'
    _description = u'Responsable légal'
    
    _columns = {
        'name': fields.char('Nom de responsable', required=True)
    }

is_responsable_legal()

class is_type_hebergement(osv.osv):
    _name = 'is.type.hebergement'
    _description = u'Type hébergement'
    
    _columns = {
        'name': fields.char(u'Type hébergement', required=True)
    }

is_responsable_legal()
    
class is_situation(osv.osv):
    _name = 'is.situation'
    _description = 'Situation familiale'
    
    _columns = {
        'name': fields.char('Situation', required=True),
    }

is_situation()

class is_usager_notification(osv.osv):
    _name = 'is.usager.notification'
    _description = 'Notifications des usagers'
    
    _columns = {
        'notif_num': fields.integer(u'Numéro'),
        'notif_date': fields.date('En date'),
        'notif_start_validity_date': fields.date(u'Date début de validité'),
        'notif_end_validity_date': fields.date(u'Date fin de validité'),
        'notif_prescripteur': fields.char('Prescripteur'),
        'attachment_ids': fields.many2many('ir.attachment', 'is_notification_attachment_rel', 'notification_id', 'attachment_id', 'Fichier'),        
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_usager_notification()

class is_usager_parent(osv.osv):
    _name = 'is.usager.parent'
    _description = 'parents'
    
    _columns = {
        'name': fields.char('Nom', required=True),
        'up_name_jf': fields.char('Nom de jeune fille'),
        'up_first_name': fields.char(u'Prénom'),
        'up_birthday': fields.date('Date de naissance'),
        'up_birth_place': fields.char('Lieu de naissance'),
        'up_gender_id': fields.many2one('is.gender', 'Sexe'),
        'up_type_id': fields.many2one('is.type.parent', 'Type', required=True),
        'up_categ_prof': fields.char(u'Catégorie socio-professionnelle'),
        'up_street': fields.char('Adresse'),
        'up_zip': fields.char('Code postal', size=24),
        'up_city': fields.char('Ville'),
        'up_phone': fields.char(u'Téléphone fixe'),
        'up_mobile': fields.char(u'Téléphone mobile'),
        'up_fax': fields.char('Fax'),
        'up_email': fields.char('Courriel'),
    }

is_usager_parent()

class is_usager_affiliation(osv.osv):
    _name = 'is.usager.affiliation'
    _description = 'Affiliations des usagers'
    
    _columns = {
        'aff_type': fields.char('Type'),
        'aff_assure': fields.char(u'Assuré'),
        'aff_assure_name': fields.char(u"Nom de l'assuré (si Assuré = Autre)"),
        'aff_num_dossier': fields.char(u'Numéro de dossier'),
        'aff_date': fields.date('En date'),
        'aff_start_validity_date': fields.date(u'Date début de validité'),
        'aff_end_validity_date': fields.date(u'Date fin de validité'),
        'affiliateur_id': fields.many2one('is.usager.parent', 'Affiliateur'),
        'aff_code': fields.char('Code'),
        'aff_organisme': fields.char('Organisme'),
        'aff_code_gestion': fields.char('Code gestion'),
        'attachment_ids': fields.many2many('ir.attachment', 'is_affiliation_attachment_rel', 'affiliation_id', 'attachment_id', 'Fichier'),
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_usager_affiliation()

class is_usager_prestation(osv.osv):
    _name = 'is.usager.prestation'
    _description = 'Prestations des usagers'
    
    _columns = {
        'prest_num_dossier': fields.char(u'Numéro de dossier'),
        'prest_date': fields.date('En date'),
        'prest_start_validity_date': fields.date(u'Date début de validité'),
        'prest_end_validity_date': fields.date(u'Date fin de validité'),
        'prestataire_id': fields.many2one('is.usager.parent', 'Prestataire'),
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_usager_prestation()

class is_usager_autorisation(osv.osv):
    _name = 'is.usager.autorisation'
    _description = 'Autorisations des usagers'
    
    _columns = {
        'aut_type': fields.char('Type'),
        'aut_date': fields.date('Date'),
        'attachment_ids': fields.many2many('ir.attachment', 'is_autorisation_attachment_rel', 'autorisation_id', 'attachment_id', 'Fichier'),
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_usager_autorisation()

class is_usager_contre_indications(osv.osv):
    _name = 'is.usager.contre.indications'
    _description = 'Contre indications'
    
    _columns = {
        'cont_nature': fields.char('Nature'),
        'cont_start_validity_date': fields.date(u'Date début de validité'),
        'cont_end_validity_date': fields.date(u'Date fin de validité'),
        'cont_professional_id': fields.many2one('res.users', u'Professionnel de santé'),
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }

is_usager_contre_indications()

class is_usager_soins(osv.osv):
    _name = 'is.usager.soins'
    _description = 'Soins'
    
    _columns = {
        'soin_nature': fields.char('Nature'),
        'soin_start_validity_date': fields.date(u'Date début de validité'),
        'soin_end_validity_date': fields.date(u'Date fin de validité'),
        'soin_professional_id': fields.many2one('res.users', u'Professionnel de santé'),
        'comment': fields.text('Commentaire'),
        'usager_id': fields.many2one('is.dossier.usager', 'Usager'),
    }
    
is_usager_soins()
