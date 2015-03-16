/// <reference path='../../all.d.ts' />


module odh.auth {
    'use strict';

    export class ValidateService {
        message = {
            'minlength': 'This value is not long enough.',
            'maxlength': 'This value is too long.',
            'email': 'A properly formatted email address is required.',
            'required': 'This field is required.'
        };
        more_messages =
        {
            'demo': {
                'required': 'Here is a sample alternative required message.'
            }
        };
        public check_more_messages(name, error) {
            return (this.more_messages[name] || [])[error] || null;
        }

        public validation_messages(field, form, error_bin) {
            var messages = [];
            for (var e in form[field].$error) {
                if (form[field].$error[e]) {
                    var special_message = this.check_more_messages(field, e);
                    if (special_message) {
                        messages.push(special_message);
                    } else if (this.message[e]) {
                        messages.push(this.message[e]);
                    } else {
                        messages.push('Error: ' + e);
                    }
                }
            }
            var deduped_messages = [];
            angular.forEach(messages, function (el, i) {
                if (deduped_messages.indexOf(el) === -1) {
                        deduped_messages.push(el);
                    }
            });
            if (error_bin) {
                error_bin[field] = deduped_messages;
            }
        }

        public form_validation(form, error_bin) {
            for (var field in form) {
                if (field.substr(0, 1) !== '$') {
                    this.validation_messages(field, form, error_bin);
                }
            }
        }


    }
    angular.module('openDataHub.auth').service('ValidateService', ValidateService);
}
