//task.js

var TASK_PAGE_SIZE = 20;

var taskJS = function(){
	var self = this;
	var room_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var room_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	this.ext_task = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;

		self.task_store = new Ext.data.JsonStore({
			url : '/get_task_list/' + self.plat + '/',
			root : 'data',
			totalProperty : 'total_count',
			remoteSort : true,
			pruneModifiedRecords: true, 
			fields : [
				{name: 'hash', type: 'string'},
				'create_time',
				'hits_num',
				'cold'
			]
		});

		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var task_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'hash', id : 'hash', dataIndex : 'hash', sortable : true},
			{header : 'create_time', id : 'create_time', dataIndex : 'create_time', sortable : true, },
			{header : 'hits_num', id : 'hits_num', dataIndex : 'hits_num', sortable : true},
			{header : 'cold', id : 'cold', dataIndex : 'cold', sortable : true, width:100},			
		]);
		
		var task_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: TASK_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
	            store: self.task_store,
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

		self.task_grid = new Ext.grid.EditorGridPanel({
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.task_store,
			colModel: 		task_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar: [{
				text: '导出热度表',
				iconCls: 'compare_down',
				handler: self.down_hot_table
			},'-',{
				text: '导出冷度表',
				iconCls: 'compare_down',
				handler: self.down_cold_table
			},'-',{				
				text: '刷新任务列表',				
				iconCls: 'refresh',
				handler: self.refresh_task_list
			},'-',{				
				text: '任务详细状态',				
				iconCls: 'detail',
				handler: self.show_task_detail
			}],
			bbar: task_page
		});
	
		self.task_store.load({params:{start:0, limit:TASK_PAGE_SIZE}});
		
		main_panel.add(self.task_grid);
		main_panel.setActiveTab(self.task_grid);
	};

	/**
	 * 刷新列表
	 */
	this.refresh_task_list = function() {
		self.task_store.reload();
	}
	
};

Task = new taskJS();
