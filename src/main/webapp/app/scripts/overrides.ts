/// <reference path='all.d.ts' />
/* tslint:disable:interface-name */
/**
 * provides an interface for the ES6 function format.
 */
interface String {
    format(...replacements:string[]):string;
}
