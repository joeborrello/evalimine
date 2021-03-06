#!/usr/bin/python2.7
# -*- coding: UTF8 -*-

"""
Copyright: Eesti Vabariigi Valimiskomisjon
(Estonian National Electoral Committee), www.vvk.ee
Written in 2004-2014 by Cybernetica AS, www.cyber.ee

This work is licensed under the Creative Commons
Attribution-NonCommercial-NoDerivs 3.0 Unported License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc-nd/3.0/.
"""

import os
import subprocess
import signal
import shutil
import sys
import traceback
import uiutil
from election import Election
from election import ElectionState
import election
import evcommon
import evreg
import burner
import autocmd
import glob

import evfiles
import serviceutil

CHOICE_ADD_DESCRIPTION = "Anna isikule kirjeldus"
CHOICE_ADD_RIGHTS = "Anna isikule volitused"
CHOICE_AUDIT = "Audit"
CHOICE_BACK = "Tagasi (Ctrl+D)"
CHOICE_BACKUP = "Varunda olekupuu ja apache logid"
CHOICE_BROWSE_FILE = "Sirvi"
CHOICE_CHANGE_ELECTION_DESCRIPTION = "Muuda valimiste kirjeldust"
CHOICE_CHECK_CONFIGURE = "Vaata konfiguratsiooni hetkeseisu"
CHOICE_CHECK_CONSISTENCY = "Kontrolli HES ja HTS serverite kooskõlalisust"
CHOICE_CONFIGURE_COMMON = "Üldine konfiguratsioon"
CHOICE_CONFIGURE = "Konfigureeri"
CHOICE_COUNT_VOTES = "Loe hääled kokku"
CHOICE_CREATE_STATUS_REPORT = "Genereeri vaheauditi aruanne"
CHOICE_CREATE_STATUS_REPORT_NO_VERIFY = \
    "Genereeri vaheauditi aruanne hääli verifitseerimata"
CHOICE_DEL_ELECTION_ID = "Kustuta valimisidentifikaator"
CHOICE_DIR_LIST = "Vaata kataloogi sisu"
CHOICE_DISABLE_VOTERS_LIST = "Keela hääletajate nimekirja kontroll"
CHOICE_ELECTION_ID = "Tegele valimistega"
CHOICE_ENABLE_VOTERS_LIST = "Luba hääletajate nimekirja kontroll"
CHOICE_EXIT = "Välju"
CHOICE_EXPORT_ALL = "Ekspordi kõik"
CHOICE_EXPORT_FILE_ALL = "Ekspordi kõik failid"
CHOICE_EXPORT_FILE_SOME = "Ekspordi mõned failid"
CHOICE_EXPORT_FILE = "Ekspordi"
CHOICE_SET_MID_CONF = "Muuda Mobiil-ID sätteid"
CHOICE_GET_HSM_CONF = "Vaata HSMi konfiguratsiooni"
CHOICE_HES_CONF = "Laadi HESi valimiste failid"
CHOICE_HLR_BACKUP = "Varunda olekupuu"
CHOICE_HLR_CONF = "Laadi HLRi valimiste failid"
CHOICE_HTS_CONF = "Laadi HTSi valimiste failid"
CHOICE_HTS_REVOKE = "Rakenda tühistus-/ennistusnimekirja"
CHOICE_IMPORT_VOTES = "Impordi hääled lugemiseks"
CHOICE_INSTALL = "Laadi valimiste seaded paigaldusfailist"
CHOICE_LIST_ALL_RIGHTS = "Vaata kõiki volitusi"
CHOICE_LIST_USER_RIGHTS = "Vaata isiku volitusi"
CHOICE_LOAD_ELECTORS = "Laadi valijate faili täiendused"
CHOICE_LOAD_STRINGS = "Laadi konfigureeritavad teated"
CHOICE_NEW_ELECTION_ID = "Loo uus valimisidentifikaator"
CHOICE_REGRIGHTS = "Volitused"
CHOICE_REM_ALL_RIGHTS = "Kustuta kõik volitused"
CHOICE_REM_RIGHTS = "Kustuta isiku volitus"
CHOICE_REM_USER_RIGHTS = "Kustuta kõik isiku volitused"
CHOICE_RESTORE_FROM_BACKUP = "Taasta olekupuu varukoopiast"
CHOICE_RESTORE_INIT_STATUS = "Taasta algolek"
CHOICE_SET_HES_HTS_CONF = "Säti HTSi konfiguratsioon"
CHOICE_SET_HSM_CONF = "Initsialiseeri HSM"
CHOICE_START_COUNTING = "Alusta lugemisperioodi"
CHOICE_PRE_START_COUNTING_HES = "Lõpeta nimekirjade väljastamine"
CHOICE_CANCEL_PRE_START_COUNTING_HES = "Taasta nimekirjade väljastamine"
CHOICE_START_COUNTING_HES = "Lõpeta hääletusperiood"
CHOICE_START_ELECTION = "Alusta hääletusperioodi"
CHOICE_START_REVOCATION = "Alusta tühistusperioodi"
CHOICE_THE_END = "Lõpeta valimised"
CHOICE_BDOC_CONF = "Laadi sertifikaatide konfiguratsioon"
CHOICE_VIEW_ELECTION_DESCRIPTION = "Vaata valimiste kirjeldust"
CHOICE_VIEW_STATUS_REPORT = "Vaata vaheauditi aruannet"
CHOICE_CONFIG_FILES_HISTORY = "Nimekirjade uuendamise ajalugu"
CHOICE_VERIFICATION_CONF = "Seadista kontrollitavus"
CHOICE_SCHEDULE_AUTOSTART = "Seadista hääletusperioodi automaatne algus"
CHOICE_UNSCHEDULE_AUTOSTART = "Kustuta hääletusperioodi automaatne algus"
CHOICE_SCHEDULE_AUTOSTOP = "Seadista hääletusperioodi automaatne lõpp"
CHOICE_UNSCHEDULE_AUTOSTOP = "Kustuta hääletusperioodi automaatne lõpp"
CHOICE_SCHEDULE_CONF = "Seadista automaatse lõpu kestvus"
CHOICE_SESSION_CONF = "Muuda valimisseansi sätteid"
CHOICE_GET_PUBLIC_KEY = "Vaata valijate faili signatuuri avalikku võtit"
CHOICE_SET_PUBLIC_KEY = "Laadi valijate faili signatuuri avalik võti"

# Konfi skriptid
SCRIPT_HTS_STATE = "hts_state.py"

# Prorgammid
PROGRAM_LESS = "less"
PROGRAM_LESS_ARGS = "-fC"

# Faili actionid
ACTION_BROWSE_FILE = "Sirvi faili"
ACTION_EXPORT_FILE = "Ekspordi fail(id)"

# Menüü pealkirjad
MENU_MAINMENU = "Peamenüü"

STR_YES = "yes"
# STR_NO =  "no"

# PID
MESSAGE_PID_EXISTS = "%s on juba olemas! Jätkamine võib lõhkuda olemasoleva operaatori menüü.\n" \
                     "Kas soovid jätkata" % autocmd.REFRESH_PID_VALUE

SHA256_KEYS = [
    evfiles.ELECTIONRESULT_STR,
    evfiles.ELECTIONRESULT_STAT_STR,
    evfiles.ELECTIONS_RESULT_STR,
    evfiles.REVREPORT_STR,
    evfiles.ELECTORSLIST_STR]


def file_action_to_str(action):

    ret = None

    if action == ACTION_BROWSE_FILE:
        return CHOICE_BROWSE_FILE
    elif action == ACTION_EXPORT_FILE:
        return CHOICE_EXPORT_FILE
    else:
        raise Exception('Defineerimata failioperatsioon')

    return ret


class MenuItemCommand:

    def __init__(self, name, action, args):
        self.__name = name
        self._action = action
        self.__args = args

    def get_str(self, idx):
        return " (%d) %s" % (idx, self.__name)

    def draw(self, idx):
        print " [%d] %s" % (idx, self.__name)

    def do_action(self, _):
        if self._action:
            if self.__args:
                self._action(self.__args)
            else:
                self._action()


class MenuItemSubMenu:

    def __init__(self):
        self.__name = None
        self.__cmd_list = []

    def create(self, name):
        self.__name = name
        self.__cmd_list = []

    def add_item(self, item, action=None, args=None):
        self.__cmd_list.append(MenuItemCommand(item, action, args))

    def draw(self, idx):
        print " [%d] %s" % (idx, self.__name)
        for k in range(len(self.__cmd_list)):
            print "\t", self.__cmd_list[k].get_str(k + 1)

    def do_action(self, cmd_string):

        if len(cmd_string) < 1:
            print "Palun tee ka alamvalik"
            return
        elif len(cmd_string) > 1:
            print "Vale valik"
            return

        idx = int(cmd_string[0]) - 1

        try:
            if idx not in range(len(self.__cmd_list)):
                print "Vale valik: %s" % cmd_string[0]
                return
        except ValueError:
            print "Vale valik: %s" % cmd_string[0]
            return

        self.__cmd_list[idx].do_action(cmd_string)


class EvUI:

    """
    Teksti moodis kasutajaliides HESi, HTSi ja HLRi tarbeks
    """

    def __init__(self):
        self.quit_flag = 0
        self.cmd_list = []
        self.__sub0 = MenuItemSubMenu()
        self.__sub1 = MenuItemSubMenu()
        self.__sub2 = MenuItemSubMenu()
        self.file_table = {}

        self.ui_update_function = None

        self.cur_elid = ""
        self.file_action = ""
        self.menu_caption = ""
        self.state = ElectionState().get()
        self.init_main_menu()

    def execute_command(self, val, cmd):
        self.cmd_list[val].do_action(cmd[1:])

    def items(self):
        return range(len(self.cmd_list))

    def add_item(self, name, action, args=None):
        self.cmd_list.append(MenuItemCommand(name, action, args))

    def add_sub(self, sub):
        self.cmd_list.append(sub)

    def clear_items(self):
        self.cmd_list = []

    def get_quit_flag(self):
        return self.quit_flag

    def init_main_menu(self):

        def create_sub0(sub):
            sub.create(CHOICE_ELECTION_ID)
            for el in Election().get_questions():
                sub.add_item(
                    "%s (%s)" % (el, Election().get_election_type_str(el)),
                    self.do_conf_election, el)

        def create_sub1_hes(sub):
            sub.create(CHOICE_CONFIGURE_COMMON)
            sub.add_item(CHOICE_BDOC_CONF, serviceutil.do_bdoc_conf_hes)
            sub.add_item(CHOICE_INSTALL, serviceutil.do_install)
            sub.add_item(CHOICE_SET_MID_CONF, serviceutil.do_set_mid_conf)
            sub.add_item(CHOICE_SET_HES_HTS_CONF, serviceutil.do_set_hts_conf)
            sub.add_item(CHOICE_SESSION_CONF, serviceutil.do_session_conf)
            sub.add_item(CHOICE_CONFIG_FILES_HISTORY,
                         serviceutil.do_config_files_history)

            if Election().is_config_hth_done():
                sub.add_item(CHOICE_CHECK_CONSISTENCY,
                             serviceutil.do_check_consistency)

            if self.state == election.ETAPP_ENNE_HAALETUST:
                if Election().is_voters_list_disabled():
                    sub.add_item(CHOICE_ENABLE_VOTERS_LIST,
                                 serviceutil.do_enable_voters_list)
                else:
                    sub.add_item(CHOICE_DISABLE_VOTERS_LIST,
                                 serviceutil.do_disable_voters_list)

            if Election().is_hes_configured():
                if self.state < election.ETAPP_HAALETUS:
                    if autocmd.scheduled(autocmd.COMMAND_START):
                        sub.add_item(CHOICE_UNSCHEDULE_AUTOSTART,
                                     serviceutil.do_unschedule_autostart)
                    else:
                        sub.add_item(CHOICE_SCHEDULE_AUTOSTART,
                                     serviceutil.do_schedule_autostart)

                if self.state == election.ETAPP_ENNE_HAALETUST:
                    sub.add_item(CHOICE_START_ELECTION, self.do_change_state)

                if self.state < election.ETAPP_LUGEMINE:
                    if (autocmd.scheduled(autocmd.COMMAND_PREPARE_STOP) or
                            autocmd.scheduled(autocmd.COMMAND_STOP)):
                        sub.add_item(CHOICE_UNSCHEDULE_AUTOSTOP,
                                     serviceutil.do_unschedule_autostop)
                    elif Election().allow_new_voters():
                        sub.add_item(CHOICE_SCHEDULE_AUTOSTOP,
                                     serviceutil.do_schedule_autostop)

            if self.state == election.ETAPP_HAALETUS:
                if Election().allow_new_voters():
                    sub.add_item(CHOICE_PRE_START_COUNTING_HES,
                                 serviceutil.do_pre_start_counting_hes)
                else:
                    sub.add_item(CHOICE_CANCEL_PRE_START_COUNTING_HES,
                                 serviceutil.do_cancel_pre_start_counting_hes)
                sub.add_item(CHOICE_START_COUNTING_HES, self.do_change_state)

        def create_sub1_hts(sub):
            sub.create(CHOICE_CONFIGURE_COMMON)
            sub.add_item(CHOICE_BDOC_CONF, serviceutil.do_bdoc_conf)
            sub.add_item(CHOICE_INSTALL, serviceutil.do_install)
            sub.add_item(CHOICE_CONFIG_FILES_HISTORY,
                         serviceutil.do_config_files_history)

            sub.add_item(CHOICE_VERIFICATION_CONF,
                         serviceutil.do_verification_conf)

            if self.state == election.ETAPP_ENNE_HAALETUST:
                if Election().is_voters_list_disabled():
                    sub.add_item(CHOICE_ENABLE_VOTERS_LIST,
                                 serviceutil.do_enable_voters_list)
                else:
                    sub.add_item(CHOICE_DISABLE_VOTERS_LIST,
                                 serviceutil.do_disable_voters_list)

            if (self.state == election.ETAPP_ENNE_HAALETUST and
                    Election().is_hts_configured()):
                sub.add_item(CHOICE_START_ELECTION, self.do_change_state)

            if self.state == election.ETAPP_HAALETUS:
                sub.add_item(CHOICE_START_REVOCATION, self.do_change_state)

            if self.state == election.ETAPP_TYHISTUS:
                sub.add_item(CHOICE_START_COUNTING, self.do_change_state)

        def create_sub1_hlr(sub):
            sub.create(CHOICE_CONFIGURE_COMMON)
            sub.add_item(CHOICE_BDOC_CONF, serviceutil.do_bdoc_conf)
            sub.add_item(CHOICE_INSTALL, serviceutil.do_install)
            sub.add_item(CHOICE_CONFIG_FILES_HISTORY,
                         serviceutil.do_config_files_history)

            sub.add_item(CHOICE_SET_HSM_CONF, serviceutil.do_set_hsm_conf)
            sub.add_item(CHOICE_GET_HSM_CONF, serviceutil.do_get_hsm_conf)
            if (self.state == election.ETAPP_ENNE_HAALETUST and
                    Election().is_hlr_configured()):
                sub.add_item(CHOICE_START_COUNTING, self.do_change_state)

        def create_sub2_hts(sub):
            retval = False
            flag_1 = self.state > election.ETAPP_ENNE_HAALETUST
            flag_2 = evfiles.statusreport_file().exists()

            if flag_1 or flag_2:
                retval = True
                sub.create(CHOICE_AUDIT)

            if flag_1:
                sub.add_item(CHOICE_CREATE_STATUS_REPORT,
                             serviceutil.do_create_status_report)
                sub.add_item(CHOICE_CREATE_STATUS_REPORT_NO_VERIFY,
                             serviceutil.do_create_status_report_no_verify)
            if flag_2:
                sub.add_item(CHOICE_VIEW_STATUS_REPORT,
                             serviceutil.do_view_status_report)
            return retval

        self.ui_update_function = self.init_main_menu
        self.menu_caption = MENU_MAINMENU
        self.cur_elid = ""
        self.clear_items()
        if self.state == election.ETAPP_ENNE_HAALETUST:
            self.add_item(CHOICE_NEW_ELECTION_ID, serviceutil.do_new_election)
            if Election().count_questions() > 0:
                self.add_item(CHOICE_DEL_ELECTION_ID,
                              serviceutil.do_del_election)

        if Election().count_questions() > 0:
            create_sub0(self.__sub0)
            self.add_sub(self.__sub0)

        if Election().is_hes():
            create_sub1_hes(self.__sub1)
            self.add_sub(self.__sub1)
            self.add_item(CHOICE_CHECK_CONFIGURE,
                          serviceutil.do_check_configure)
            self.add_item(CHOICE_EXPORT_ALL, self.do_export_all)
            self.add_item(CHOICE_BACKUP, serviceutil.do_backup)
            self.add_item(CHOICE_RESTORE_FROM_BACKUP, serviceutil.do_restore)
            self.add_item(CHOICE_DIR_LIST, serviceutil.do_dir_list)

            if self.state == election.ETAPP_LUGEMINE:
                self.add_item(CHOICE_THE_END, self.do_the_end)

            if self.state == election.ETAPP_HAALETUS:
                self.add_item(CHOICE_RESTORE_INIT_STATUS,
                              serviceutil.do_restore_init_status)

            self.add_item(CHOICE_LOAD_STRINGS,
                          serviceutil.do_import_error_strings)

            self.add_item(CHOICE_EXIT, self.do_quit)

        elif Election().is_hts():
            create_sub1_hts(self.__sub1)
            self.add_sub(self.__sub1)
            self.add_item(CHOICE_CHECK_CONFIGURE,
                          serviceutil.do_check_configure)
            if create_sub2_hts(self.__sub2):
                self.add_sub(self.__sub2)
            self.add_item(CHOICE_EXPORT_ALL, self.do_export_all)
            self.add_item(CHOICE_BACKUP, serviceutil.do_backup)
            self.add_item(CHOICE_RESTORE_FROM_BACKUP, serviceutil.do_restore)
            self.add_item(CHOICE_DIR_LIST, serviceutil.do_dir_list)

            if self.state == election.ETAPP_LUGEMINE:
                self.add_item(CHOICE_THE_END, self.do_the_end)

            if self.state == election.ETAPP_HAALETUS:
                self.add_item(CHOICE_RESTORE_INIT_STATUS,
                              serviceutil.do_restore_init_status)
            self.add_item(CHOICE_LOAD_STRINGS,
                          serviceutil.do_import_error_strings)
            self.add_item(CHOICE_EXIT, self.do_quit)

        elif Election().is_hlr():
            create_sub1_hlr(self.__sub1)
            self.add_sub(self.__sub1)
            self.add_item(CHOICE_CHECK_CONFIGURE,
                          serviceutil.do_check_configure)
            self.add_item(CHOICE_EXPORT_ALL, self.do_export_all)
#            self.add_item(CHOICE_HLR_BACKUP, serviceutil.do_backup)
#            self.add_item(CHOICE_RESTORE_FROM_BACKUP, serviceutil.do_restore)
            self.add_item(CHOICE_DIR_LIST, serviceutil.do_dir_list)
            if self.state == election.ETAPP_LUGEMINE:
                self.add_item(CHOICE_THE_END, self.do_the_end)
            self.add_item(CHOICE_EXIT, self.do_quit)

    def init_election_menu(self):

        def create_sub1(sub):
            sub.create(CHOICE_CONFIGURE)
            sub.add_item(CHOICE_REGRIGHTS, self.init_reg_rights_menu)

            if Election().is_hes():
                if (self.state == election.ETAPP_ENNE_HAALETUST and
                        Election().is_config_bdoc_done()):
                    sub.add_item(CHOICE_HES_CONF,
                                 serviceutil.do_hes_conf,
                                 self.cur_elid)

                if (self.state != election.ETAPP_LUGEMINE and
                        Election().is_config_server_elid_done(self.cur_elid)):
                    sub.add_item(CHOICE_LOAD_ELECTORS,
                                 serviceutil.do_load_electors,
                                 self.cur_elid)

                if Election().is_config_voter_public_key_elid_done(
                        self.cur_elid):
                    sub.add_item(CHOICE_SET_PUBLIC_KEY,
                                 serviceutil.do_set_voter_public_key,
                                 self.cur_elid)
                    sub.add_item(CHOICE_GET_PUBLIC_KEY,
                                 serviceutil.do_get_voter_public_key,
                                 self.cur_elid)

            if Election().is_hts():
                sub.add_item(CHOICE_VIEW_ELECTION_DESCRIPTION,
                             serviceutil.do_view_election_description,
                             self.cur_elid)

                if self.state == election.ETAPP_ENNE_HAALETUST:
                    sub.add_item(CHOICE_CHANGE_ELECTION_DESCRIPTION,
                                 serviceutil.do_change_election_description,
                                 self.cur_elid)
                    if Election().is_config_bdoc_done():
                        sub.add_item(CHOICE_HTS_CONF,
                                     serviceutil.do_hts_conf, self.cur_elid)

                if (self.state not in [election.ETAPP_TYHISTUS,
                                       election.ETAPP_LUGEMINE] and
                        Election().is_config_server_elid_done(self.cur_elid)):
                    sub.add_item(CHOICE_LOAD_ELECTORS,
                                 serviceutil.do_load_electors, self.cur_elid)

                if Election().is_config_voter_public_key_elid_done(
                        self.cur_elid):
                    sub.add_item(CHOICE_SET_PUBLIC_KEY,
                                 serviceutil.do_set_voter_public_key,
                                 self.cur_elid)

                    sub.add_item(CHOICE_GET_PUBLIC_KEY,
                                 serviceutil.do_get_voter_public_key,
                                 self.cur_elid)

            if Election().is_hlr():
                if Election().is_config_bdoc_done():
                    sub.add_item(CHOICE_HLR_CONF,
                                 serviceutil.do_hlr_conf,
                                 self.cur_elid)
                if Election().is_config_server_done():
                    sub.add_item(CHOICE_IMPORT_VOTES,
                                 serviceutil.do_import_votes,
                                 self.cur_elid)

        self.ui_update_function = self.init_election_menu
        self.menu_caption = "%s->%s \"%s\" (%s)" % \
            (MENU_MAINMENU, CHOICE_ELECTION_ID, self.cur_elid,
             Election().get_election_type_str(self.cur_elid))
        self.clear_items()

        create_sub1(self.__sub1)
        self.add_sub(self.__sub1)
        if Election().is_hes():
            self.add_item(CHOICE_BROWSE_FILE, self.do_browse)
            self.add_item(CHOICE_EXPORT_FILE, self.do_export)
            self.add_item(CHOICE_BACK, self.init_main_menu)

        if Election().is_hts():
            if self.state == election.ETAPP_TYHISTUS:
                self.add_item(CHOICE_HTS_REVOKE,
                              serviceutil.do_revoke, self.cur_elid)
            self.add_item(CHOICE_BROWSE_FILE, self.do_browse)
            self.add_item(CHOICE_EXPORT_FILE, self.do_export)
            self.add_item(CHOICE_BACK, self.init_main_menu)

        elif Election().is_hlr():
            if (self.state == election.ETAPP_LUGEMINE and
                    Election().is_config_hlr_input_elid_done(self.cur_elid)):
                self.add_item(CHOICE_COUNT_VOTES,
                              serviceutil.do_count_votes, self.cur_elid)
            self.add_item(CHOICE_BROWSE_FILE, self.do_browse)
            self.add_item(CHOICE_EXPORT_FILE, self.do_export)
            self.add_item(CHOICE_BACK, self.init_main_menu)

    def init_file_menu(self):
        self.ui_update_function = self.init_file_menu
        self.menu_caption = "%s->%s \"%s\"->%s" % (
            MENU_MAINMENU, CHOICE_ELECTION_ID, self.cur_elid,
            file_action_to_str(self.file_action))
        self.clear_items()
        keys = sorted(self.file_table.keys())
        for key in keys:
            if self.file_action == ACTION_EXPORT_FILE:
                self.add_item(key, self.do_file_action_one_wsha, key)
            else:
                self.add_item(key, self.do_file_action_one, key)

        if len(self.file_table) > 1:
            if self.file_action == ACTION_EXPORT_FILE:
                self.add_item(CHOICE_EXPORT_FILE_ALL,
                              self.do_file_action_all_wsha)

            if self.file_action == ACTION_EXPORT_FILE:
                self.add_item(CHOICE_EXPORT_FILE_SOME,
                              self.do_file_action_some_wsha)

        self.add_item(CHOICE_BACK, self.init_election_menu)

    def init_reg_rights_menu(self):
        self.ui_update_function = self.init_reg_rights_menu
        self.menu_caption = "%s->%s \"%s\"->%s" % (
            MENU_MAINMENU, CHOICE_ELECTION_ID, self.cur_elid, CHOICE_REGRIGHTS)
        self.clear_items()
        self.add_item(CHOICE_ADD_RIGHTS,
                      serviceutil.do_add_rights, self.cur_elid)
        self.add_item(CHOICE_ADD_DESCRIPTION,
                      serviceutil.do_add_description, self.cur_elid)
        self.add_item(CHOICE_REM_RIGHTS,
                      serviceutil.do_rem_rights, self.cur_elid)
        self.add_item(CHOICE_REM_USER_RIGHTS,
                      serviceutil.do_rem_user_rights, self.cur_elid)
        self.add_item(CHOICE_REM_ALL_RIGHTS,
                      serviceutil.do_rem_all_rights, self.cur_elid)
        self.add_item(CHOICE_LIST_USER_RIGHTS,
                      serviceutil.do_list_user_rights, self.cur_elid)
        self.add_item(CHOICE_LIST_ALL_RIGHTS,
                      serviceutil.do_list_all_rights, self.cur_elid)
        self.add_item(CHOICE_BACK, self.init_election_menu)

    def do_conf_election(self, args):
        self.cur_elid = args
        self.init_election_menu()

    def do_the_end(self):
        srv = Election().get_server_str()
        is_hlr = (srv == evcommon.APPTYPE_HLR)
        root_dir = Election().get_root_reg().root
        if uiutil.ask_yes_no("Kas soovid valimised lõpetada?"):
            if uiutil.ask_yes_no(
                "Valimiste lõpetamisega kustutatakse kogu " +
                    "konfiguratsioon.\nKas jätkan"):
                print "Kustutan e-hääletuse faile. Palun oota.."
                # Kustutame kogu konfiguratsiooni ja ka olekupuu taastamise
                # käigus alles hoitud vanad olekupuud.
                uiutil.clear_dir(root_dir)
                map(shutil.rmtree, glob.iglob("%s/../registry-*" % root_dir))
                # HLRi korral ka vastav mälufailisüsteemi kraam.
                if is_hlr:
                    if "EVOTE_TMPDIR" in os.environ:
                        uiutil.clear_dir(os.environ["EVOTE_TMPDIR"])
                # Initsialiseerime nüüd ka liidese.
                Election().set_server_str(srv)
                self.__init__()

    def do_quit(self):
        self.quit_flag = 1

    def draw(self):
        state_str = str(election.G_STATES[self.state])
        if self.state == 4 and Election().is_hes():
            state_str = "Hääletusperioodi lõpp"
        print "-----------------------------------------------------"
        print " %s\n Olek: %s" % (self.menu_caption, state_str)
        print "-----------------------------------------------------"

        for i in self.items():
            self.cmd_list[i].draw(i + 1)

    # Failidega seotud commandid
    def do_browse(self):
        self.file_action = ACTION_BROWSE_FILE
        self.init_file_menu()

    def do_export(self):
        self.file_action = ACTION_EXPORT_FILE
        self.init_file_menu()

    def do_file_action_one(self, args=None):
        self.do_file_action([self.file_table[args]])

    def get_sha256_file(self, key):
        if key in SHA256_KEYS or key.find("tokend.") == 0:
            sha256_file = self.file_table[key] + ".sha256"
            if os.access(sha256_file, os.F_OK):
                return sha256_file
        return None

    def do_file_action_one_wsha(self, args=None):
        files = []
        files.append(self.file_table[args])
        sha256f = self.get_sha256_file(args)
        if sha256f:
            files.append(sha256f)
        self.do_file_action(files)

    def do_file_action_all(self):
        self.do_file_action(self.file_table.values())

    def do_file_action_all_wsha(self):
        files = []
        for el in self.file_table:
            files.append(self.file_table[el])
            sha256f = self.get_sha256_file(el)
            if sha256f:
                files.append(sha256f)
        self.do_file_action(files)

    def do_file_action_some_wsha(self):
        keys = sorted(self.file_table.keys())
        numlist = uiutil.ask_int_list(
            "Sisesta eksporditavate failide numbrid komadega eraldatult",
            len(keys))

        if len(numlist) > 0:
            print "Valitud failid: "

        files = []
        for el in numlist:
            key = keys[el]
            print "\t%s" % key
            files.append(self.file_table[key])
            sha256f = self.get_sha256_file(key)
            if sha256f:
                files.append(sha256f)

        self.do_file_action(files)

    def do_file_action(self, args):

        if not args:
            return

        if self.file_action == ACTION_BROWSE_FILE:
            for el in args:
                subprocess.call([PROGRAM_LESS, PROGRAM_LESS_ARGS, el])
        elif self.file_action == ACTION_EXPORT_FILE:
            cd_burner = burner.FileListBurner(evcommon.burn_buff())
            try:
                if len(args) > 1:
                    print "Ekspordin failid.."
                else:
                    print "Ekspordin faili.."
                print "Palun oota.."
                if cd_burner.append_files(self.cur_elid, args):
                    cd_burner.burn()
            finally:
                cd_burner.delete_files()

    def do_export_all(self):
        """Kõigi valimiste väljund failid CDle
        """
        if Election().count_questions() < 1:
            print "Ei ole midagi eksportida"
            return
        cd_burner = burner.FileListBurner(evcommon.burn_buff())
        try:
            print "Ekspordime kõik. Palun oota.."
            for i in Election().get_questions():
                self.update_files(i)
                file_list = self.file_table.values()
                # Olukord, kus valimiste ID on, aga faile pole
                if len(file_list) == 0:
                    print "Ei ole midagi eksportida"
                    return

                # Kui on, siis ka vastav sha256 fail exporti
                for file_key in self.file_table.keys():
                    sha256f = self.get_sha256_file(file_key)
                    if sha256f:
                        file_list.append(sha256f)
                if not cd_burner.append_files(i, file_list):
                    return
            cd_burner.burn()
        finally:
            cd_burner.delete_files()

    def do_change_state(self):
        if not uiutil.ask_yes_no("Kas oled kindel"):
            return
        ElectionState().next()
        if Election().is_hts():
            subprocess.call(SCRIPT_HTS_STATE)

    def execute(self, cmd):
        if len(cmd) < 1:
            return
        try:
            val = int(cmd[0]) - 1
        except ValueError:
            print "Palun sisesta valiku number"
            return
        if val in self.items():
            try:
                self.execute_command(val, cmd)
            except KeyboardInterrupt:
                print "\nKatkestame tegevuse.."
            except EOFError:
                print "\nKatkestame tegevuse.."
            except Exception as what:
                traceback.print_exc(None, sys.stdout)
                print "Tegevus nurjus: %s" % what
        else:
            print "Tundmatu valik: %s" % cmd[0]

    def update(self):
        self.state = ElectionState().get()
        use_binary = self.file_action != ACTION_BROWSE_FILE
        self.update_files(self.cur_elid, use_binary)
        if self.ui_update_function:
            self.ui_update_function()

    def update_files(self, elid, usebinary=True):
        """
        Siin hoiame up-to-date faili tabelit, mida saab
        sirvida/printida/exportida
        """
        self.file_table = {}  # string : path

        files = evfiles.EvFileTable()
        if Election().is_hes():
            files.add_file(evfiles.application_log_file())
            files.add_file(evfiles.error_log_file())
            files.add_file(evfiles.integrity_log_file())
            files.add_file(evfiles.voter_list_log_file())
        elif Election().is_hts():
            files.add_file(evfiles.log1_file(elid))
            files.add_file(evfiles.log2_file(elid))
            files.add_file(evfiles.log3_file(elid))
            files.add_file(evfiles.revlog_file(elid))
            files.add_file(evfiles.application_log_file())
            files.add_file(evfiles.error_log_file())
            files.add_file(evfiles.voter_list_log_file())
            files.add_file(evfiles.elections_result_file(elid))
            files.add_file(evfiles.electorslist_file(elid))
            files.add_file(evfiles.electorslist_file_pdf(elid))
            files.add_file(evfiles.revreport_file(elid))
            files.add_file(evfiles.statusreport_file())
            files.add_file(evfiles.ocsp_log_file())
            evfiles.add_hts_files_to_table(elid, files)
        elif Election().is_hlr():
            files.add_file(evfiles.log4_file(elid))
            files.add_file(evfiles.log5_file(elid))
            files.add_file(evfiles.application_log_file())
            files.add_file(evfiles.error_log_file())
            files.add_file(evfiles.electionresult_zip_file(elid))
            files.add_file(evfiles.electionresult_file(elid))
            files.add_file(evfiles.electionresultstat_file(elid))

        self.file_table = files.get_existing_files(usebinary)


class RefreshSignal(Exception):
    pass


def usr1_handler(signal, frame):
    """Handler for SIGUSR1 sent by the automatic election start script."""
    raise RefreshSignal


def write_pid():
    reg = evreg.Registry(root=evcommon.EVREG_CONFIG)
    reg.ensure_key(autocmd.REFRESH_PID_KEY)
    try:
        pid = reg.read_integer_value(autocmd.REFRESH_PID_KEY,
                                     autocmd.REFRESH_PID_VALUE)
    except (IOError, LookupError):
        pid = None

    # If a PID exists and the user does not want to continue, return None.
    if pid and not uiutil.ask_yes_no(MESSAGE_PID_EXISTS, uiutil.ANSWER_NO):
        return None
    return reg.create_integer_value(autocmd.REFRESH_PID_KEY,
                                    autocmd.REFRESH_PID_VALUE,
                                    os.getpid())


def main():
    # Ignoreerime SIGTSTP, st. Ctrl+Z, Ctrl+C ja Aborti
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGABRT, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)

    pid = write_pid()
    if not pid:
        return

    evui = EvUI()
    uiutil.clrscr()

    prompt = "%sOperaator> " % Election().get_server_str()

    while not evui.get_quit_flag():
        try:
            signal.signal(signal.SIGUSR1, usr1_handler)
            evui.update()
            evui.draw()
            cmd = raw_input(prompt)
        except KeyboardInterrupt:
            # Siin püüame Ctrl+C kinni
            cmd = str(len(evui.cmd_list))
        except EOFError:
            print ""
            if evui.menu_caption == MENU_MAINMENU:
                continue
            else:
                cmd = str(len(evui.cmd_list))
        except RefreshSignal:
            print
            continue
        signal.signal(signal.SIGUSR1, signal.SIG_IGN)
        evui.execute(cmd.split())

    try:
        pid.delete()
    except OSError:
        pass  # pid file has been deleted

    # Kustutame ka CD-lt importimisel tekitatud ajutised failid
    uiutil.del_tmp_files()
    print "Head aega!\n"


if __name__ == "__main__":
    main()

# vim:set ts=4 sw=4 et fileencoding=utf8:
