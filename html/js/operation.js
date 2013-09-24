//operation.js

var OPERATION_PAGE_SIZE = 20;

var operationJS = function(){
	var self = this;
	var operation_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var operation_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
			
	this.ext_operation = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;
					
		self.operation_store = new Ext.data.JsonStore({
			url: '/get_operation_list/' + self.plat + '/',			
			root: 'data',
			totalProperty: 'total_count',
			remoteSort: true,
			pruneModifiedRecords: true, 		//必须为true，这样重新reload数据时，会将脏数据清除
			fields : [
				{name: 'id', type: 'int'},
				'type',
				'name',
				'user',
				'dispatch_time',
				'status',
				'begin_time',
				'end_time',				
				'memo'
			]
		});
					
		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var operation_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'id', id : 'id', dataIndex : 'id', sortable : true},
			{header : 'type', id : 'type', dataIndex : 'type', sortable : true},
			{header : 'name', id : 'name', dataIndex : 'name', sortable : true},
			{header : 'user', id : 'user', dataIndex : 'user', sortable : true},
			{header : 'dispatch_time', id : 'dispatch_time', dataIndex : 'dispatch_time', sortable : true},
			{header : 'status', id : 'status', dataIndex : 'status', sortable : true, renderer: operation_status},
			{header : 'begin_time', id : 'begin_time', dataIndex : 'begin_time', sortable : true},
			{header : 'end_time', id : 'end_time', dataIndex : 'end_time', sortable : true},
			{header : 'memo', id : 'memo', dataIndex : 'memo', sortable : true, width: 320}
		]);
		
		
		var operation_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: OPERATION_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
	            store: self.operation_store,
	            displayInfo: true,
	            displayMsg: ' 显示第{0}条 到 {1}条记录， 共 {2}条',
	            emptyMsg: "没有记录",
	            prevText: "上一页",
                nextText: "下一页",
                refreshText: "刷新",
                lastText: "最后页",
                firstText: "第一页",
                beforePageText: "当前页",
                afterPageText: "共{0}页"
		});
		
		self.operation_grid = new Ext.grid.EditorGridPanel({
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.operation_store,
			colModel: 		operation_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar: [{
				id: 'refresh_operation_list',
				text: '刷新操作列表',				
				iconCls: 'refresh',
				handler: self.refresh_operation_list
			},'-',{
				id: 'do_selected_operations',
				text: '执行选中操作',				
				iconCls: 'confirm',
				handler: self.do_selected_operations
			},'-',{
				id: 'do_all_operations',
				text: '执行全部操作',				
				iconCls: 'check',
				handler: self.do_all_operations
			},'-',{
				id: 'show_operation_detail',
				text: '操作详细信息',				
				iconCls: 'detail',
				handler: self.show_operation_detail
			}],
			bbar: operation_page
		});
		
		self.operation_store.load({params:{start:0,limit:OPERATION_PAGE_SIZE}});
		
		main_panel.add(self.operation_grid);
		main_panel.setActiveTab(self.operation_grid);			

		function operation_status(value) {
			switch(value) {
				case "0": return '<span class="green">0</span>'; break;
				default:
					return '<span class="red">' + value  + '</span>';
			}
		}

		//右键触发事件
		function rightClickRowMenu(grid, rowIndex, cellIndex, e) {
			e.preventDefault();//禁用浏览器默认的右键，针对某一行禁用
			if (rowIndex < 0)
				return true;
			var record = grid.getStore().getAt(rowIndex);//获取当前行的纪录
			var server_id = record.get('server_id');

			var t_sm = grid.getSelectionModel();

			//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
			//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
			var server_id_arr = []
			if (t_sm.getSelected()) {
				var recs = t_sm.getSelections();
				for (var i = 0; i < recs.length; i++) {
					server_id_arr.push(recs[i].get('server_id'));
				}
			}
			var param_id = '';
			if (server_id_arr.indexOf(server_id) < 0) {
				//当前行没有选中
				t_sm.clearSelections();
				t_sm.selectRow(rowIndex);
				grid.getView().focusRow(rowIndex);
				param_id = server_id;
			} else {
				param_id = server_id_arr.join(',');
			}

			//如果存在右键菜单，清楚菜单里的所有项
			if (Ext.get('server_right_menu')) {
				Ext.getCmp('server_right_menu').removeAll();
			}
			//生成右键菜单
			//Ext.Ajax.request({
			//	url: '/server/get_options/',
			//});
		}
		
		//给控键添加右键菜单触发事件
		self.operation_grid.addListener('cellcontextmenu', rightClickRowMenu);
		self.operation_grid.addListener('contextmenu', function(e){e.preventDefault(); })//禁用浏览器默认的右键，针对grid禁用
		
		
	};
			
	this.refresh_operation_list = function() 
	{		
		self.operation_store.reload();
	}
	
	this.do_selected_operations = function() {
		var grid = self.operation_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var operation_ids = []
		if (t_sm.getSelected()) 
		{
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) 
			{
				operation_ids.push(recs[i].get('id'));
			}
		}
		else
		{
			return;
		}
		//console.log(ms_ips);

		Ext.Ajax.request({
			url: '/do_selected_operations/' + self.plat + '/',				
			params: 'ids=' + operation_ids,
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);						
				
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', response.responseText);
			}
			//timeout: (this.timeout*1000);
		});

	};
	
	this.do_all_operations = function() {
		
		Ext.Ajax.request({
			url: '/do_all_operations/' + self.plat + '/',				
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);						
				
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', response.responseText);
			}
			//timeout: (this.timeout*1000);
		});

	};

	this.show_operation_detail = function() {
		var grid = self.operation_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var operation_ids = []
		if (t_sm.getSelected()) 
		{
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) 
			{
				operation_ids.push(recs[i].get('id'));
			}
		}
		else
		{
			return;
		}
		//console.log(ms_ips);

		Ext.Ajax.request({
			url: '/show_operation_info/' + self.plat + '/',				
			params: 'ids=' + operation_ids,
			success: function(response) {
				//Ext.MessageBox.alert('成功', Ext.encode(response));	
				//console.log(response.responseText);				
				var ms_panel = new Ext.Panel({
				  //renderTo: 'panelDiv',
				  title: '操作状态: ' + operation_ids,
				  iconCls : 'tabs',
	    		  closable : true,
	    		  autoScroll: true,
				  items:[{
				    html: response.responseText
				  }]
				});
				var main_panel = Ext.getCmp("main_panel");
				main_panel.add(ms_panel);
				main_panel.setActiveTab(ms_panel);		
				
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
	
};

Operation = new operationJS();
