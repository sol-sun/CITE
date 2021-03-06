{
    // Ext.container
    Ext.require('Ext.container.Viewport');
    // Ext.grid
    Ext.require('Ext.grid.plugin.RowEditing');
    Ext.require('Ext.grid.Panel');
    Ext.require('Ext.grid.column.RowNumberer');
    // Ext.form
    Ext.require('Ext.form.field.ComboBox');
    Ext.require('Ext.form.FieldSet');
    Ext.require('Ext.form.RadioGroup');
    // Ext.layout

    Ext.require('Ext.layout.container.*');
    // Ext.tab
    Ext.require('Ext.tab.Panel');
    // Ext.app
    Ext.require('Ext.app.ViewController');
    // Ext.widget
    Ext.require('Ext.menu.ColorPicker');
    // Ext.data
    Ext.require('Ext.data.Store');
    Ext.require('Ext.form.field.File');
    Ext.require('Ext.form.field.HtmlEditor');
}

Ext.onReady(function(){
    Ext.tip.QuickTipManager.init();
    
    Ext.define('KitchenSink.view.form.FileUploadsController', {
        extend: 'Ext.app.ViewController',
        alias: 'controller.form-fileuploads',
    
        firstFormSave: function() {
            var form = this.lookupReference('basicFile').getForm();
            var editor = form.findField('html');

            if (form.isValid()) {form.submit({
                method:'POST',
                url: './Script/file-upload.cgi',
                waitMsg: 'Searching your input articles...',
                success: function(fp, o) {
                    var tpl = new Ext.XTemplate(
                        '<b>Response</b>: {fileName}<br />'
                    );
                    editor.getEditorBody().innerHTML += o.result.Reference +'<br>';
                    Ext.MessageBox.show({
                        title: '<b>Success<b>',
                        message: tpl.apply(o.result),
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.INFO
                    });
                },
                failure: function(fp, o){
                    var tpl = new Ext.XTemplate(
                        '<b>{description}</b><br />'
                    );
                
                    Ext.MessageBox.show({
                        title: '<b>Error<b>',
                        message: tpl.apply(o.result),
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.ERROR
                    });
                }
            });
                                }
        }
    });


     var NorthPanel = Ext.create('Ext.panel.Panel', {
        region:'north',
        xtype: 'panel',
        bodyStyle: 'background-color:#1b3450;color: gray;',
        height: 40,
        border: false,
        autoHeight: true,
        id: 'north-region-container',
        html: '<div id="hoge" style="float:left;font-size:9px;color:white;"><h1 class="x-panel-header">&nbspCITE: Reference Generator for academic articles&nbsp(ver &alpha;)</h1></div>'
     });
    
    var CenterPanel =  Ext.create('Ext.container.Container',{
        region: 'center',
        xtype: 'form-fileuploads',
        controller: 'form-fileuploads',
        autoWidth: true,
        layout: {
            type: 'vbox',
            align: 'stretch'
        },
        defaults: {
            xtype: 'form',
            layout: 'anchor',
            
            bodyPadding: 10,
            style: {
                'margin-bottom': '20px'
            },
            
            defaults: {
                anchor: '100%'
            }
        },
        items: [{
    
            reference: 'basicFile',
            items: [{
                xtype: 'component',
                html: [
                    '<h3>Please Input your file(Alpha version)</h3>',
                    '<p>現在以下のアウトプットに対応しています...',
                    '<ul>',
                    '<li><code>Bioinformatics</code></li>',
                    '<li><code>Nucleic Acid Research</code></li>',
                    '<li><code>BibTeX</code></li>',
                    '</ul>',
                ]
            }, {
                xtype: 'combobox',
                emptyText: 'Select the output format...',
                name: 'output-format',
                editable: false,
                allowBlank: false,
                store:[
                    [ 'bioinformatics','Bioinformatics'],
                    [ 'nucleic_acids_research','Nucleic Acids Research'],
                    [ 'bibtex', 'BibTeX']
                ]
                
            },{
                xtype: 'filefield',
                hideLabel: true,
                name: 'photo-path'
                
            },{
                xtype: 'button',
                text: 'Submit',
                handler:  'firstFormSave'
            },{
                xtype: 'htmleditor',
                title: 'HTML Editor',
                name:'html',
                autoWidth:true,
                frame:true,
                id:'HTML',
                layout:'fit',
                enableAlignments: false,
                enableColors: true
            }
                
            ]
        }]
    });

    var EastPanel = Ext.create('Ext.panel.Panel', {
         id: 'east-region-container',
        region: 'south',
        title: '',
        collapsed: true,
        collapsible: true,
        split: true,
        height: 500,
        layout: 'fit'
    });

 Ext.define('CITE.Viewport', {
        extend: 'Ext.container.Viewport',
        layout: 'border',
     items: [ NorthPanel, CenterPanel,EastPanel],
        renderTo: Ext.getBody()
 });
    Ext.create('CITE.Viewport');
});
