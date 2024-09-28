import json

from frameworks.FrameworkPageBuilder import FrameworkPageBuilder

        
if __name__ == "__main__":
    import constants as _C
    from utils.Config import Config
    
    Config.init()
    Config.set('cli_services', {'ec2': 2, 'iam': 1, 'cloudfront': 5})
    Config.set('cli_frameworks', ['WAFS'])
    Config.set('cli_regions', ['ap-southeast-1'])
    
    samples = [['Main', 'ARC-002', 0, [], []], ['Main', 'ARC-003', -1, "<dl><dt><i class='fas fa-times'></i> [rootMfaActive]</dt><dd>Enable MFA on root user<br><small>{'GLOBAL': ['User::<b>root_id</b>']}</small></dd><dt><i class='fas fa-times'></i> [mfaActive]</dt><dd>Enable MFA on IAM user.<br><small>{'GLOBAL': ['User::ttttt']}</small></dd></dl>", "<a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a><br><a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a>"], ['Main', 'IAM-001', -1, "<dl><dt><i class='fas fa-times'></i> [mfaActive]</dt><dd>Enable MFA on IAM user.<br><small>{'GLOBAL': ['User::ttttt']}</small></dd></dl>", "<a href='https://aws.amazon.com/iam/features/mfa/'>AWS Docs</a>"], ['Main', 'IAM-002', 1, "<dl><dt><i class='fas fa-check'></i> [passwordLastChange90]</i></dt><dt><i class='fas fa-check'></i> [passwordLastChange365]</i></dt></dl>", ''], ['Main', 'IAM-003', -1, "<dl><dt><i class='fas fa-times'></i> [passwordPolicyWeak]</dt><dd>Set a stronger password policy<br><small>{'GLOBAL': ['Account::Config']}</small></dd><dt><i class='fas fa-check'></i> [passwordPolicy]</i></dt></dl>", "<a href='https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#configure-strong-password-policy'>AWS Docs</a>"], ['Main', 'IAM-007', 1, "<dl><dt><i class='fas fa-check'></i> [consoleLastAccess90]</i></dt><dt><i class='fas fa-check'></i> [consoleLastAccess365]</i></dt></dl>", '']]
    
    data = json.loads(open(_C.FRAMEWORK_DIR + '/api.json').read())
    o = FrameworkPageBuilder('WAFS', data)
    p = o.buildPage()
    # print(p)