/**
 * JavaScript pour le portail client de gestion de parc informatique
 */
odoo.define('parc_IT.portal', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    
    // S'assurer que ces modules sont disponibles, sinon retourner un Widget vide
    if (!publicWidget || !core) {
        console.warn("Les modules requis n'ont pas été chargés correctement pour parc_IT.portal");
        return {};
    }
    
    var _t = core._t;

    publicWidget.registry.ParcITPortal = publicWidget.Widget.extend({
        selector: '.parc_it_portal',
        events: {
            'click .equipment-details': '_onEquipmentClick',
            'click .intervention-details': '_onInterventionClick',
            'click .contract-details': '_onContractClick',
            'click .create-intervention-request': '_onCreateInterventionRequest',
        },

        /**
         * @override
         */
        start: function() {
            return this._super.apply(this, arguments);
        },

        /**
         * Gère le clic sur un équipement dans le portail
         * @param {Event} ev
         * @private
         */
        _onEquipmentClick: function (ev) {
            ev.preventDefault();
            var equipmentId = $(ev.currentTarget).data('equipment-id');
            window.location = '/my/equipment/' + equipmentId;
        },

        /**
         * Gère le clic sur une intervention dans le portail
         * @param {Event} ev
         * @private
         */
        _onInterventionClick: function (ev) {
            ev.preventDefault();
            var interventionId = $(ev.currentTarget).data('intervention-id');
            window.location = '/my/intervention/' + interventionId;
        },

        /**
         * Gère le clic sur un contrat dans le portail
         * @param {Event} ev
         * @private
         */
        _onContractClick: function (ev) {
            ev.preventDefault();
            var contractId = $(ev.currentTarget).data('contract-id');
            window.location = '/my/contract/' + contractId;
        },

        /**
         * Gère le clic pour créer une demande d'intervention
         * @param {Event} ev
         * @private
         */
        _onCreateInterventionRequest: function (ev) {
            ev.preventDefault();
            window.location = '/my/intervention/create';
        },
    });

    return publicWidget.registry.ParcITPortal;
}); 