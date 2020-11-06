from sqlalchemy import desc

from rootio.config import *
from rootio.content.models import ContentPodcast, ContentPodcastDownload
from .utils.audio import PlayStatus


class PodcastAction:

    def __init__(self, podcast_id, start_time, duration, program):
        self.__podcast_id = podcast_id
        self.__podcast_download = None
        self.__is_valid = True
        self.start_time = start_time
        self.duration = duration
        self.program = program
        self.__media_expected_to_stop = False
        self.__call_answer_info = None
        self.__call_handler = self.program.radio_station.call_handler
        self.program.log_program_activity("Done initialising Podcast action for program {0}".format(self.program.name))

    def start(self):
        self.program.set_running_action(self)
        try:
            self.__load_podcast()
            if self.__podcast_download is not None:
                call_result = self.__request_station_call()
                # CARLOS - is this supposed to be a no_media status?
                if call_result is None or not call_result[0]:  # !!
                    self.stop(PlayStatus.no_media)
            else:
                self.stop(PlayStatus.no_media)
        except Exception as e:
            self.stop(PlayStatus.failed)
            self.program.radio_station.logger.error("error {err} in podcast_action.__start".format(err=e.message))

    def pause(self):
        self.__pause_media()

    def stop(self, status_type=PlayStatus.success, call_info=None):
        if call_info is not None:
            self.__stop_media(call_info)
        elif self.__call_answer_info is not None:
            self.__stop_media(self.__call_answer_info)
        self.__deregister_listeners()
        self.program.notify_program_action_stopped(status_type, call_info)

    def notify_call_answered(self, answer_info):
        self.program.log_program_activity(
            "Received call answer notification for podcast action of {0} program".format(self.program.name))
        self.__call_answer_info = answer_info
        self.__call_handler.register_for_call_hangup(self, answer_info['Caller-Destination-Number'][-11:])
        self.__play_media(self.__call_answer_info)

    def __load_podcast(self):  # load the media to be played
        self.__podcast_download = self.program.radio_station.db.query(ContentPodcastDownload).filter(
            ContentPodcastDownload.podcast_id == self.__podcast_id).order_by(desc(ContentPodcastDownload.date_published)).first()
        #self.__podcast.podcast_downloads.sort(key=lambda x: x.date_published, reverse=True)

    def __request_station_call(self):  # call the number specified thru plivo
        # Check if the call exists, start with the least likely number to be called
        if self.program.radio_station.station.secondary_transmitter_phone is not None and self.__call_handler.call_exists(
                self.program.radio_station.station.secondary_transmitter_phone.raw_number):
            result = self.__call_handler.call(self,
                                              self.program.radio_station.station.secondary_transmitter_phone.raw_number,
                                              self.program.name, False, self.duration)
            return result
        elif self.program.radio_station.station.primary_transmitter_phone is not None and self.__call_handler.call_exists(
                self.program.radio_station.station.primary_transmitter_phone.raw_number):
            result = self.__call_handler.call(self,
                                              self.program.radio_station.station.primary_transmitter_phone.raw_number,
                                              self.program.name, False, self.duration)
            return result
        elif self.program.radio_station.station.sip_username is not None and self.__call_handler.call_exists(
                self.program.radio_station.station.sip_username):
            result = self.__call_handler.call(self, self.program.radio_station.station.sip_username, self.program.name,
                                              True, self.duration)
            self.program.log_program_activity("result of station call via SIP is " + str(result))
            return result

        # At this point we are sure that no call to the station exists. We will try to initiate a new call
        if self.program.radio_station.station.is_high_bandwidth:
            result = self.__call_station_via_sip()
            if result is None or not result[0]:  # Now try calling the SIM (ideally do primary, then secondary)
                result = self.__call_station_via_goip()
        else:
            result = self.__call_station_via_goip()
        return result

    def __call_station_via_sip(self):
        # Try a high bandwidth call first
        if self.program.radio_station.station.sip_username is not None:
            result = self.__call_handler.call(self, self.program.radio_station.station.sip_username, self.program.name,
                                              True,
                                              self.duration)
            self.program.log_program_activity("result of station call via SIP is " + str(result))
            return result

    def __call_station_via_goip(self):
        result = None
        if self.program.radio_station.station.primary_transmitter_phone is not None:
            result = self.__call_handler.call(self,
                                              self.program.radio_station.station.primary_transmitter_phone.raw_number,
                                              self.program.name, False,
                                              self.duration)
            self.program.log_program_activity("result of station call (primary) via GoIP is " + str(result))
            if not result[
                0] and self.program.radio_station.station.secondary_transmitter_phone is not None:  # Go for the secondary line of the station, if duo SIM phone
                result = self.__call_handler.call(self,
                                                  self.program.radio_station.station.secondary_transmitter_phone.raw_number,
                                                  self.program.name, False,
                                                  self.duration)
                self.program.log_program_activity("result of station call (secondary) via GoIP is " + str(result))
        return result

    def __play_media(self, call_info):  # play the media in the array
        self.program.log_program_activity("Playing media {0}".format(
            self.__podcast_download.file_name))
        self.__listen_for_media_play_stop()

        # Always play the last file for news
        result = self.__call_handler.play(call_info['Channel-Call-UUID'],
                                          os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast_download.podcast_id),
                                                       self.__podcast_download.file_name))

        self.program.log_program_activity('result of play is ' + result)
        if result.split(" ")[0] != "+OK":
            self.stop(PlayStatus.failed, call_info)

    def __pause_media(self):  # pause the media in the array
        pass

    def __stop_media(self, event_json):  # stop the media being played by the player
        try:
            self.program.log_program_activity(
                "Deregistered, all good, about to order hangup for {0}".format(self.program.name))
            result = self.__call_handler.stop_play(self.__call_answer_info['Channel-Call-UUID'],
                                                   os.path.join(DefaultConfig.CONTENT_DIR, 'podcast',
                                                                str(self.__podcast_download.podcast_id),
                                                                self.__podcast_download.file_name))
            self.program.log_program_activity('result of stop play is ' + result)
        except Exception as e:
            self.program.radio_station.logger.error("error {err} in podcast_action.__stop_media".format(err=e.message))
        self.stop(PlayStatus.success, event_json)

    def notify_call_hangup(self, event_json):
        self.program.log_program_activity('Call hangup before end of program!')
        self.__request_station_call()

    def notify_media_play_stop(self, event_json):
        try:
            self.program.radio_station.logger.info(
                "Played all media, stopping media play in Media action for {0}".format(self.program.name))
            self.__is_valid = False
        except Exception as e:
            self.program.radio_station.logger.error("error {err} in podcast_action.notify_media_play_stop".format(err=e.message))
        self.stop(PlayStatus.success, event_json)

    def __listen_for_media_play_stop(self):
        self.__call_handler.register_for_media_playback_stop(self,
                                                             self.__call_answer_info['Caller-Destination-Number'][-11:])

    def __deregister_listeners(self):
        if self.__call_answer_info is not None:
            self.__call_handler.deregister_for_media_playback_stop(
                self.__call_answer_info['Caller-Destination-Number'][-11:])
            self.__call_handler.deregister_for_call_hangup(self.__call_answer_info['Caller-Destination-Number'][-11:])