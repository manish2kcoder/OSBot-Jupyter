from pbx_gs_python_utils.utils.slack.Slack_Commands_Helper import Slack_Commands_Helper


def run(event, context):
    try:
        from osbot_aws.apis.Lambda import load_dependency
        load_dependency('requests')

        channel = event.get('channel')
        team_id = event.get('team_id')
        params  = event.get('params')

        if params and len(params) == 1: params = []     # todo: this case (when the last param is the events data), needs to be handled by Jupyter_Web_Commands

        from osbot_jupyter.osbot.Jupyter_Web_Commands import Jupyter_Web_Commands

        result = Slack_Commands_Helper(Jupyter_Web_Commands).invoke(team_id, channel, params)
        if channel is None:
            return result

    except Exception as error:
        message = "[jupyter_web] Error: {0}".format(error)
        return message