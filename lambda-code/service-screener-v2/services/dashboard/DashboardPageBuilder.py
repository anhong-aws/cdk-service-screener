import datetime
from services.PageBuilder import PageBuilder
from utils.Config import Config
import utils.Config as cfg

class DashboardPageBuilder(PageBuilder):
    def init(self):
        self.isHome = True
        self.template = 'dashboard'
        
    def buildContentSummary_dashboard(self):
        output = []
        items = []
        dataSets = {
            'S': {'T': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0},
            'R': {'T': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0},
            'C': {'T': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0},
            'P': {'T': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0},
            'O': {'T': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0}
        }
        
        hriSets = {
            'H': 0,
            'M': 0,
            'L': 0,
            'I': 0
        }
        
        dashboard = cfg.dashboard.copy()
        
        total = 0
        if not 'CRITICALITY' in dashboard:
            print("0 recommendations detected, expecting empty report")
            return
        
        for region, details in dashboard['CRITICALITY'].items():
            for cat, cnt in details.items():
                if not cat == 'X':
                    hriSets[cat] += cnt
                    
                total += cnt
        
        for cat, count in hriSets.items():
            items.append(self.getHRIInfo(cat, count, total))
        
        for region, details in dashboard['CATEGORY'].items():
            for cat, grp in details.items():
                if cat == 'T':
                    continue
                
                if not cat == 'X':
                    for sev, cnt in grp.items():
                        dataSets[cat][sev] += cnt
                        dataSets[cat]['T'] += cnt
        
        xhtml = "<dl class='row'>" + '\n'.join(items) + "</dl>"
        items = []
        
        pid = self.getHtmlId('criticalityCount')
        card = self.generateCard(pid=pid, html=xhtml, cardClass='danger', title='No. Criticality', titleBadge='', collapse=False, noPadding=False)
        securityBox = self.generateSecurityBigBox(dataSets['S'])
        
        customHtml = f"""
<div class="row">
    <div class="col-sm-8">
        {card}
    </div>
    {securityBox}
</div>
"""
        output.append(customHtml)
        
        for cat, total in dataSets.items():
            if cat == 'S' or cat == 'T':
                continue
            items.append([self.getDashboardCategoryTiles(cat, total), ''])
        
        output.append(self.generateRowWithCol(size=3, items=items, rowHtmlAttr="data-context='pillars'"))
        
        return output
        
    def buildContentDetail_dashboard(self):
        ## Chart - Categorise by Services, Stacked by Region
        items = {}
        serviceLabels = [] 
        regionLabels = []
        donutL = {}
        donutR = {} 
        dataSetsL = {}
        dataSetsR = {}
        filterDonutL = {}
        filterDonutR = {}
        
        regions = self.regions
        services = self.services

        for service, cnt in services.items():
            serviceLabels.append(service)
            dataSetsR[service] = []
            donutR[service] = 0
            
        for region in regions:
            regionLabels.append(region)
            dataSetsL[region] = []
            donutL[region] = 0
            
        dashboard = cfg.dashboard.copy()
            
        for serv, attrs in dashboard['SERV'].items():
            for region in regions:
                hri = cnt = 0
                if region in attrs:
                    cnt = attrs[region]['Total']
                    hri = attrs[region]['H']
                
                dataSetsL[region].append(cnt)
                dataSetsR[serv].append(cnt)
                donutL[region] += hri
                donutR[serv] += hri
        
        for region, cnt in donutL.items():
            if cnt > 0:
                filterDonutL[region] = cnt
        
        for serv, cnt in donutR.items():
            if cnt > 0:
                filterDonutR[serv] = cnt
                
        
        # card = self.generateCard(pid=pid, html=html, cardClass='danger', title='No. Criticality', titleBadge='', collapse=False, noPadding=False)
                
        html = self.generateDonutPieChart(filterDonutL, 'hriByRegion', 'doughnut')
        card = self.generateCard(pid=self.getHtmlId('chartServRegion'), html=html, cardClass='warning', title='High Risk - Group by Region', titleBadge='', collapse=True, noPadding=False)
        items = [[card, '']]
        
        html = self.generateDonutPieChart(filterDonutR, 'hriByService', 'pie')
        card = self.generateCard(pid=self.getHtmlId('pieHriByService'), html=html, cardClass='warning', title='High Risk - Group by Service', titleBadge='', collapse=True, noPadding=False)
        items.append([card, ''])
        
        output = [self.generateRowWithCol(size=6, items=items, rowHtmlAttr="data-context='chartHRICount'")]
        
        items = []
        html = self.generateBarChart(serviceLabels, dataSetsL, 'csr')
        card = self.generateCard(pid=self.getHtmlId('chartServRegion'), html=html, cardClass='info', title='Chart by Serv by Region', titleBadge='', collapse=True, noPadding=False)
        items.append([card, ''])
        
        html = self.generateBarChart(regionLabels, dataSetsR, 'crs')
        card = self.generateCard(pid=self.getHtmlId('chartRegionServ'), html=html, cardClass='info', title='Chart by Region by Serv', titleBadge='', collapse=True, noPadding=False)
        items.append([card, ''])
        
        output.append(self.generateRowWithCol(size=6, items=items, rowHtmlAttr="data-context='chartCount'"))
        
        output.append("<h6>Report generated at <u>{}</u>, timezone setting: {}</h6>".format(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), 'UTC'))
        return output
        
    def getDashboardCategoryTiles(self, key, cnt):
        colorArr = {
            'S': ['danger', 'Security', 'cog'],
            'R': ['fuchsia', 'Reliability', 'globe'],
            'C': ['primary', 'Cost Optimization', 'dollar-sign'],
            'P': ['success', 'Performance Efficiency', 'seedling'],
            'O': ['navy', 'Operation Excellence', 'wrench']
        }
        
        colorClass, title, icon = colorArr[key]
        
        style = "style='color: #dfdfdf'" if key == 'O' else ""
        
        total = cnt['T']
        highCnt = cnt['H']
        mediumCnt = cnt['M']
        lowCnt = cnt['L']
        infoCnt = cnt['I']
        
        output = f"""
<div class="small-box bg-{colorClass}" style="cursor:pointer;" onClick="window.open('CPFindings.html#{title}', '_blank')">
  <div class="inner">
    <h3>{total}</h3>
    <p>{title}</p>
  </div>
  <div class="icon">
    <i {style} class="fas fa-{icon}"></i>
  </div>
  <div class="row" style="
    background-color: rgba(0,0,0,.1);
    text-align: center;
    margin: 1px;
    ">
    <div class="col-lg-3 col-sm-6"><i class="fas fa-ban"></i> {highCnt}</div>
    <div class="col-lg-3 col-sm-6"><i class="fas fa-exclamation-triangle"></i> {mediumCnt}</div>
    <div class="col-lg-3 col-sm-6"><i class="fas fa-eye"></i> {lowCnt}</div>
    <div class="col-lg-3 col-sm-6"><i class="fas fa-info-circle"></i> {infoCnt}</div>
  </div>
</div>
"""
        return output
        
    def getHRIInfo(self, cat, cnt, total):
        attrArr = {
            'H': ['danger', 'High', 'ban'],
            'M': ['warning', 'Medium', 'exclamation-triangle'],
            'L': ['info', 'Low', 'eye'],
            'I': ['primary', 'Informational', 'info-circle']
        }
        
        colorClass, title, icon = attrArr[cat]
        
        percentile = round(cnt * 100 / total)
        
        output = f"""
<dt class="col-sm-4"><a style='cursor: pointer; color: black;' target=_blank rel='noopener noreferrer' href='CPFindings.html#{title}'><i class="fas fa-{icon}"></i> {title}</dt></a>
<dd class="col-sm-8" style='text-align: right'>{cnt}</dd>
<dt class="col-sm-12">
<div class="progress mb-3">
  <div class="progress-bar bg-{colorClass}" role="progressbar" aria-valuenow="{percentile}" aria-valuemin="0"
	   aria-valuemax="100" style="width: {percentile}%">
	<span>({percentile}%)</span>
  </div>
</div>
</dt>    
"""
        return output
        
    def generateSecurityBigBox(self, cnt):
        total = cnt['T']
        highCnt = cnt['H']
        mediumCnt = cnt['M']
        lowCnt = cnt['L']
        infoCnt = cnt['I']
        
        output = f"""
<div class="col-sm-4" style="cursor:pointer;" onClick="window.open('CPFindings.html#Security', '_blank')">
	<div class="small-box bg-danger" style='height: 357px'>
	  <div class="inner">
		<h3>{total}</h3>
		<p>Security</p>
	  </div>
	  <div class="icon">
		<i style='color: #dfdfdf' class="fas fa-skull-crossbones"></i>
	  </div>
	  <div class="row" style="background-color: rgba(0,0,0,.1); text-align: center; font-size:26px; margin: 1px; margin-top: 167px">
	    <div class="col-lg-6 col-sm-6"><i class="fas fa-ban"></i> {highCnt}</div>
        <div class="col-lg-6 col-sm-6"><i class="fas fa-exclamation-triangle"></i> {mediumCnt}</div>
        <div class="col-lg-6 col-sm-6"><i class="fas fa-eye"></i> {lowCnt}</div>
        <div class="col-lg-6 col-sm-6"><i class="fas fa-info-circle"></i> {infoCnt}</div>
	  </div>
	</div>
</div>
"""
        return output