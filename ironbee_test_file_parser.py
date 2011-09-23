# -*- coding: utf-8 -*-
#############################################################################
##                                                                         ##
## Licensed to Qualys, Inc. (QUALYS) under one or more                     ##
## contributor license agreements.  See the NOTICE file distributed with   ##
## this work for additional information regarding copyright ownership.     ##
## QUALYS licenses this file to You under the Apache License, Version 2.0  ##
## (the "License"); you may not use this file except in compliance with    ##
## the License.  You may obtain a copy of the License at                   ##
##                                                                         ##
##     http://www.apache.org/licenses/LICENSE-2.0                          ##  
##                                                                         ##
## Unless required by applicable law or agreed to in writing, software     ##
## distributed under the License is distributed on an "AS IS" BASIS,       ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.##
## See the License for the specific language governing permissions and     ##
## limitations under the License.                                          ##
#############################################################################

import sys
import traceback
from ironbee_test_utils import *
import json
import re
import sys
from pprint import pprint
import nids

class FileParser:
    #Parse Ivan's Evasion Test Format
    def ivan_evasion_test(self,file):
        payload = ""
        rules = []
        try:
            lines = open(file, "r").readlines()
        except:
            print("failed to parse file %s" % (file))
            sys.exit(-1)
        for line in lines:
            if re.match(r"^\s*#", line) != None:
                m = re.match(r'^\s*#\s*@\s*(?P<rule_result>\S+)(\s+(?P<match_location>\S+)\s+(?P<match_re>\S+))?', line)
                if m != None:
                    rules.append({})
                    print "found rule\n result:%s location:%s regex:%s" % (m.group('rule_result'), m.group('match_location'), m.group('match_re'))
                    if m.group('match_location') != None and m.group('match_re') != None:
                        rules[-1]['result'] = m.group('rule_result')
                        rules[-1]['location'] = m.group('match_location')
                        rules[-1]['regex'] = m.group('match_re')
                        rules[-1]['regex_obj'] = re.compile(rules[-1]['regex'])
                    else:
                        rules[-1]['result'] =  m.group('rule_result')
                        rules[-1]['location'] = None   
                else:
                    print "comment line but not rule:\n%s" % (line)
                next
            else:
                if re.match(r'(.*[^\r]\n$|^\n$)', line) != None:
                    line = re.sub(r'\n', '\r\n', line)
                    print "replacing line"
                payload += "%s" % (line)
        print payload
        return (payload, rules)
    
    #Parse a pcap file using tshark    
    def pcap_tshark(self,file):
        print "Not yet implemented"

    #Parse nikto2 variables file.
    def nikto2_vars(self,file):
        self.nikto_vars = {}
        lines = open(file).readlines()
        for line in lines:
            m = re.match(r'^(?P<var_name>@([^=])+)=(?P<var_list>.+)$',line)
            if m != None:
                self.nikto_vars[m.group('var_name')] = m.group('var_list').split(' ')
        return self.nikto_vars
                  
    #Parse Nikto2 test db format       
    def nikto2_db(self,options,file):
        self.nikto_list = []
        #http://cirt.net/nikto2-docs/expanding.html
        lines = open(file).readlines()
        for line in lines:
            for key in options.nikto_vars_parsed:
                 if key in line:
                     for replacement in options.nikto_vars_parsed[key]:
                         newline = line.replace(key, replacement)
                         
                         m = re.match(r'^\"(?P<test_id>[0-9]+)\"\,\"(?P<osvdb_id>[0-9]+)\"\,\"(?P<server_matching>[a-z0-9]+)?\"\,\"(?P<http_uri>([^\"]|(?<=\\)\")+)\"\,\"(?P<http_method>[A-Za-z]+)\"\,\"(?P<match>([^\"]|(?<=\\)\")+)\"\,\"(?P<match_or>([^\"]|(?<=\\)\")+)?\"\,\"(?P<match_and>([^\"]|(?<=\\)\")+)?\"\,\"(?P<fail>([^\"]|(?<=\\)\")+)?\"\,\"(?P<fail_or>([^\"]|(?<=\\)\")+)?\"\,\"(?P<summary>([^\"]|(?<=\\)\")+)\"\,\"(?P<http_data>([^\"]|(?<=\\)\")+)?\"\,\"(?P<http_headers>([^\"]|(?<=\\)\")+)?\"$',newline)
                         if m != None:
                             self.nikto_list.append({'test_id':m.group('test_id'),'ovsvdb_id':m.group('osvdb_id'),'server_matching':m.group('server_matching'),'http_uri':urllib.quote(m.group('http_uri'), safe="%/:=&?~#+!$,;'@()*[]"),'http_method':m.group('http_method'),'match':m.group('match'),'match_or':m.group('match_or'),'match_and':m.group('match_and'),'summary':m.group('summary'),'http_data':m.group('http_data'),'http_headers':m.group('http_headers')})            
                         else:
                             options.log.error("non-matching line:\n%s" % (newline))
                 else:
                     m = re.match(r'^\"(?P<test_id>[0-9]+)\"\,\"(?P<osvdb_id>[0-9]+)\"\,\"(?P<server_matching>[a-z0-9]+)?\"\,\"(?P<http_uri>([^\"]|(?<=\\)\")+)\"\,\"(?P<http_method>[A-Za-z]+)\"\,\"(?P<match>([^\"]|(?<=\\)\")+)\"\,\"(?P<match_or>([^\"]|(?<=\\)\")+)?\"\,\"(?P<match_and>([^\"]|(?<=\\)\")+)?\"\,\"(?P<fail>([^\"]|(?<=\\)\")+)?\"\,\"(?P<fail_or>([^\"]|(?<=\\)\")+)?\"\,\"(?P<summary>([^\"]|(?<=\\)\")+)\"\,\"(?P<http_data>([^\"]|(?<=\\)\")+)?\"\,\"(?P<http_headers>([^\"]|(?<=\\)\")+)?\"$',line)
                     if m != None:
                         self.nikto_list.append({'test_id':m.group('test_id'),'ovsvdb_id':m.group('osvdb_id'),'server_matching':m.group('server_matching'),'http_uri':urllib.quote(m.group('http_uri'), safe="%/:=&?~#+!$,;'@()*[]"),'http_method':m.group('http_method'),'match':m.group('match'),'match_or':m.group('match_or'),'match_and':m.group('match_and'),'summary':m.group('summary'),'http_data':m.group('http_data'),'http_headers':m.group('http_headers')})            
                     else:
                         options.log.error("non-matching line:\n%s" % (line))
        #print self.nikto_list
        #sys.exit(-1)
        return self.nikto_list
                 
    def handleTcpStream(self,tcp):
        if tcp.nids_state == nids.NIDS_JUST_EST:
            ((src, sport), (dst, dport)) = tcp.addr
            tcp.client.collect = 1
            tcp.server.collect = 1
        elif tcp.nids_state == nids.NIDS_DATA:
            tcp.discard(0)
        elif tcp.nids_state in (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET):
            toserver = tcp.server.data[:tcp.server.count]
            toclient = tcp.client.data[:tcp.client.count]
            ((src, sport), (dst, dport)) = tcp.addr
            try:
                m = re.match(r'^(?P<http_method>[A-Z]+)\s+(?P<http_uri>.+)\s+HTTP\/(?P<http_version>\d\.\d)\r?\n',toserver)
                if m != None:
                    #print "%s:%s -> %s:%s" % (src,sport,dst,dport)
                    #print("method:%s http_uri:%s http_version:%s" % (m.group('http_method'), m.group('http_uri'), m.group('http_version')))
                    #print toserver
                    self.pcap_list.append(toserver)
            except:
                print "failed to print toserver data %s" % (tcp.nids_state)

    #Parse a pcap file using libnids
    def parse_pcap(self,options,file):
        try:
            import nids
        except:
            options.log.error("failed to import LibNIDS are you sure it's installed")
            sys.exit(-1)

        self.pcap_list = []
        
        if options.pcap_bpf != None:
            nids.param("pcap_filter", options.pcap_bpf)
            
        nids.param("scan_num_hosts", 0)
        nids.param("filename", file)
        nids.init()
        nids.register_tcp(self.handleTcpStream)
        try:
            nids.run()
        except nids.error, e:
            options.log.error("nids/pcap error:" % (e))
        except Exception, e:
            options.log.error("misc. exception (runtime error in user callback?):" % (e))
        return self.pcap_list

    def parse_ironbee_mime_headers(self,header_lines):
        headers_dict={}
        for line in header_lines:
            m_header = re.match(r'^(?P<header_name>[^\r\n]+)\:\s*(?P<header_value>[^\r\n]+)\r?\n$',line)
            if m_header != None:
                headers_dict[m_header.group('header_name')] = m_header.group('header_value')
            else:
                print "non-matching header line in headers"
        return headers_dict 
    
    def get_ironbee_mime_part_name(self,headers_dict):
        if headers_dict.has_key('Content-Disposition'):
            m_name = re.match(r'^\s*audit-log-part;\s*name=\"(?P<part_name>[^\"\r\n]+)\"\s*$',headers_dict['Content-Disposition'])
            if m_name != None:
                return m_name.group('part_name')
            else:
                print("found content-disposition header but could not extract part name")
                return None
        else:
            print("could not find content-disposition header")
            return None
    
    #parse an ironbee multi_part_mime_message
    def parse_ironbee_multi_part_mime(self,options,file,boundary=None):
        sub_parts = deepdict()
        sub_parts_by_name = deepdict()
        request = {}
        boundary = ""
        end_boundary = ""
        sub_part_cntr = 0
        
        try:  
            lines = open(file, "r").readlines()
        except:
            options.log.error("failed to parse file %s" % (file))
            sys.exit(-1)
        
        
        #First we have to find our boundary if it was not supplied to us
        #If it was supplied create the end boundary.
        if boundary == "":
            for line in lines:
               m = re.match(r'^(?P<boundary>--[^\r\n]+)(?P<line_sep>\r?\n?)$',line, re.DOTALL)
               if m != None:
                   line_sep = m.group('line_sep')
                   boundary = m.group('boundary') + line_sep
                   end_boundary = m.group('boundary') + "--" + line_sep
                   options.log.debug("boundary set to :%s" % (boundary))
                   options.log.debug("end_boundary set to:%s" % (end_boundary))
                   break
               else:
                   next
               
            if boundary == "":
                options.log.debug("%s could not find a valid boundary in this document i.e. line starting with --" % (file))
                sys.exit(-1)
                
        else:
            #TODO: This probably isn't safe across OS's we should regex match anchored to the start of the line
            boundary = boundary + "\n" 
            end_boundary =boundary + "--\n"
            
        hit_first_boundary = False
        part_headers_end_seen = False
        
        for line in lines:
            if not hit_first_boundary:
                if line == boundary:
                    hit_first_boundary = True
                    options.log.debug("found first boundary")
                    part_headers_end_seen = False
                    sub_parts[sub_part_cntr]['all_lines'] = []
                    sub_parts[sub_part_cntr]['header_lines'] = []
                    sub_parts[sub_part_cntr]['body_lines'] = []
                    print sub_parts
                    next
                else:
                    options.log.debug("skipping line %s" % (line))
                    next
            else:
                if line == boundary:
                    part_headers_end_seen = False
                    sub_part_cntr = sub_part_cntr + 1
                    sub_parts[sub_part_cntr]['all_lines'] = []
                    sub_parts[sub_part_cntr]['header_lines'] = []
                    sub_parts[sub_part_cntr]['body_lines'] = []
                elif line == end_boundary:
                    options.log.debug("finished parsing parts with boundary %s" % (boundary))
                else:
                    if not part_headers_end_seen:
                        if re.match(r'^[\r\n]+$',line)!= None:
                            part_headers_end_seen = True
                            next
                        else:
                            options.log.debug("part %s:trying append header line %s" % (sub_part_cntr,line))
                            sub_parts[sub_part_cntr]['header_lines'].append(line)
                    else:
                        options.log.debug("part %s:trying append body line %s" % (sub_part_cntr,line))
                        sub_parts[sub_part_cntr]['body_lines'].append(line)
                        
                    sub_parts[sub_part_cntr]['all_lines'].append(line)
                    
        #parse the sub parts in order as         
        i = 0
        while i <= sub_part_cntr:
            #store the header and bodies as one complete buffer by joining the lines
            sub_parts[i]['header_buffer'] = ''.join(sub_parts[i]['header_lines'])
            sub_parts[i]['body_buffer'] = ''.join(sub_parts[i]['body_lines'])
            
            options.log.debug("sub_part_id:%s\nheader_lines:\n%s\nbody_lines:\n%s" % (i,sub_parts[i]['header_buffer'],sub_parts[i]['body_buffer']))
            #get the headers as a key/value pair
            sub_parts[i]['headers_dict'] = self.parse_ironbee_mime_headers(sub_parts[i]['header_lines'])
            
            #If we have json_data parse it so that we can work with it. Parsed data will be stored in json_data
            if sub_parts[i]['headers_dict'].has_key('Content-Type'):
                if sub_parts[i]['headers_dict']['Content-Type'] == 'application/json':
                    try:
                        sub_parts[i]['json_data'] = json.loads(sub_parts[i]['body_buffer'])
                        options.log.debug("parsed_json:\n%s\n" % (sub_parts[i]['json_data']))
                    except:
                        options.log.error("failed to parse json data:\n%s\n" % (sub_parts[i]['body_buffer']))
                         
            sub_parts[i]['name'] = self.get_ironbee_mime_part_name(sub_parts[i]['headers_dict'])
            
            options.log.debug("part name:%s" % (sub_parts[i]['name']))
            
            #store the parts by name instead of by part id
            sub_parts_by_name[sub_parts[i]['name']] = sub_parts[i]              
            i = i + 1
    
        return sub_parts_by_name

    def modsec_audit_log(options,file):
        lines = open(file).readlines()
        current_tid = None
        current_part_val = None
        current_part_buf = ""
        req_dict = {}
        for line in lines:
            if current_tid == None:
                m = re.match(r'^--(?P<tid>[a-zA-Z0-9]+)-A--$',line)
                if m:
                    current_tid = m.group('tid')
                    current_part_val = "A"
                else:
                    next
            else:
                m = re.match(r'^--%s-(?P<part>[BCDEFGHIJK])--$' % current_tid,line)
                if m:
                     if current_part_val == 'B':
                         #print current_part_val
                         #print current_part_buf
                         req_dict[current_tid] = current_part_buf
                     elif current_part_val == 'C':
                         #print current_part_buf
                         req_dict[current_tid] = req_dict[current_tid] + current_part_buf  
                         print req_dict[current_tid]                                
                     current_part_val = None
                     current_part_buf = ""
                     current_part_val = m.group('part')
                elif re.match(r'^--%s-Z--$' % current_tid,line) != None:
                     current_tid = None
                     current_part_val = None
                     current_part_buf = "" 
                else:
                     current_part_buf = current_part_buf + line    
        return req_dict

    def parse_ironbee_audit_log_index(self,options,file):
        lines = open(file).readlines()
        file_list = []
        for line in lines:
            if self.file_from_audit_log_index_line(index_file,options,line) != None:
                file_list.append("%s%s" % (os.path.dirname(file),m.group('filename')))
        return file_list
    
    def file_from_audit_log_index_line(self,options,index_file,line):
        #127.0.0.1:9931 127.0.0.1 - - [-] "-" 0 0 "-" "-" 4dc98781-17f1-426f-8fff-60f901234567 "-" /20110510/1844/4dc98781-17f1-426f-8fff-60f901234567.log 0 0 -
        m = re.match(r'^(?P<hostname>\S+) (?P<remote_host>\S+) (?P<remote_username>\S+) (?P<local_username>\S+) (?P<date>\[.*\]) \"(?P<request>.*)\" (?P<status>\S+) (?P<bytes_out>\S+) \"(?P<referer>.*)\" \"(?P<user_agent>.*)\" (?P<unique_id>\S+) \"(?P<session_id>.*)\" (?P<filename>\S+) (?P<offset>\d+) (?P<size>\d+) (?P<hash>\S+)(?P<extra>.*)$',line)
        if m:
            filename = ("%s%s" % (os.path.dirname(index_file),m.group('filename')))
            return filename
        else:
            options.log.error("non-matching ironbee audit log index line %s" % (line))
            return None
    
    def ironbee_test_file(self,options,file):
        disabled_list = []
        try:
            fh = open(file)
            tmp_dict = json.load(fh)
            fh.close()
        except:
            traceback.print_exc(file=sys.stdout)
            options.log.error('Failed to load JSON from ironbee test file %s' % file)
            sys.exit(-1)
            
        for test in tmp_dict:
            if options.ironbee_test_regex and re.match(r'%s' % options.ironbee_test_regex, test) == None:
                disabled_list.append(test)
                next
                
            if tmp_dict[test].has_key('enabled') and tmp_dict[test]['enabled'].lower() == "true":
                if not tmp_dict[test].has_key('normalize'):
                    options.log.warning('%s does not have a \'normalize\' key defaulting to true' % (test))
                    tmp_dict[test]['normalize'] = True
                elif tmp_dict[test]['normalize'].lower() == "true":
                    tmp_dict[test]['normalize'] = True
                elif tmp_dict[test]['normalize'].lower() == "false":
                    tmp_dict[test]['normalize'] = False
                else:
                    options.log.error('%s does not have a valid \'normalize\' key of \'%s\' only True and False excepted' % (test,tmp_dict[test]['normalize']))
                    sys.exit(-1)
                    
                if not tmp_dict[test].has_key('matches'):
                    options.log.error('%s does not have a \'match\' key you must specify something to match on' % (test))
                    sys.exit(-1)
                elif not (tmp_dict[test]['matches'].has_key('file_matches') or tmp_dict[test]['matches'].has_key('response_matches')):
                    options.log.error('%s does not contain a support match key \'match\' currently supported options are file_matches and response_matches' % (test))                
                    sys.exit(-1)
                
                if(tmp_dict[test]['matches'].has_key('file_matches')):
                    for file_match in tmp_dict[test]['matches']['file_matches']:
                        for type in options.match_types:
                            if tmp_dict[test]['matches']['file_matches'][file_match].has_key(type):
                                tmp_list = []
                                
                                for regex in tmp_dict[test]['matches']['file_matches'][file_match][type]:
                                    tmp_list.append(regex.replace('\\\\','\\'))
                            
                                #replace the list to deal with json escapes
                                tmp_dict[test]['matches']['file_matches'][file_match][type] = tmp_list
                            
                            if tmp_dict[test]['matches']['file_matches'][file_match].has_key('format'):
                                if tmp_dict[test]['matches']['file_matches'][file_match]['format'] not in options.file_match_types:
                                    options.log.error('%s:The file format %s is unknown supported options are \"text\" or \"ironbee_audit_log_index\"' % (test,file_match))
                                    sys.exit(-1)   
                            else:
                                options.log.warning('%s:You did not specify a file format for %s defaulting to text' % (test,file_match))
                                tmp_dict[test]['matches']['file_matches'][file_match]['format'] = "text"                                                           
                            
                if(tmp_dict[test]['matches'].has_key('response_matches')):
                    for response_match in tmp_dict[test]['matches']['response_matches']:
                        if response_match in options.response_match_types:
                            for type in options.match_types:
                                if tmp_dict[test]['matches']['response_matches'][response_match].has_key(type):
                                    tmp_list = []
                                    
                                    for regex in tmp_dict[test]['matches']['response_matches'][response_match][type]:
                                        tmp_list.append(regex.replace('\\\\','\\'))
                                
                                    #replace the list to deal with json escapes
                                    tmp_dict[test]['matches']['response_matches'][response_match][type] = tmp_list       
                        else:
                            options.log.error('unsupported response match type %s' % response_match)
                            sys.exit(-1)
            else:
                disabled_list.append(test)
                
        for test in disabled_list:
            del tmp_dict[test]
            options.log.error('skipping test %s as it is not enabled or does not match test regex' % test)
            
        return tmp_dict
    
    def parse_raw_request_from_file(self,options,file):
        try:
            request = open(file).read()
        except:
            options.log.error("failed to read raw request from file %s" % (file))
            sys.exit(-1)
        return request       
                
