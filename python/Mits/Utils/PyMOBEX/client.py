#!/usr/bin/env python



"""

client.py - Client classes for sending OBEX requests and handling responses.



Copyright (C) 2007 David Boddie <david@boddie.org.uk>



This file is part of the PyOBEX Python package.



This program is free software: you can redistribute it and/or modify

it under the terms of the GNU General Public License as published by

the Free Software Foundation, either version 3 of the License, or

(at your option) any later version.



This program is distributed in the hope that it will be useful,

but WITHOUT ANY WARRANTY; without even the implied warranty of

MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

GNU General Public License for more details.



You should have received a copy of the GNU General Public License

along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""



from common import OBEX_Version

import headers

import requests

import responses





class Client(object):



    """Client

    

    client = Client(address, port)

    

    Provides common functionality for OBEX clients, including methods for

    connecting to and disconnecting from a server, sending and receiving

    headers, and methods for higher level actions such as "get", "put",

    "set path" and "abort".

    

    The address used is a standard six-field bluetooth address, and the port

    should correspond to the port providing the service you wish to access.

    """

    

    def __init__(self, mitsConnection):

    

        self.max_packet_length = 0x2000

        self.obex_version = OBEX_Version()

        self.response_handler = responses.ResponseHandler()

        

        self.con = mitsConnection

        self.connection_id = None

    

    def _send_headers(self, request, header_list, max_length):

    

        """Convenience method to add headers to a request and send one or

        more requests with those headers."""

        

        # Ensure that any Connection ID information is sent first.

        if self.connection_id:

            header_list.insert(0, self.connection_id)

        

        while header_list:

        

            if request.add_header(header_list[0], max_length):

                header_list.pop(0)

            else:

                self.con.send(request.encode())

                

                if isinstance(request, requests.Connect):

                    response = self.response_handler.decode_connection(self.con)

                else:

                    response = self.response_handler.decode(self.con)

                

                if not isinstance(response, responses.Continue):

                    return response

                

                request.reset_headers()

        

        # Always send at least one request.

        if isinstance(request, requests.Get):

            # Turn the last Get request containing the headers into a

            # Get_Final request.

            request.code = requests.Get_Final.code

        

        self.con.send(request.encode())



        print "Request",

        if isinstance(request, requests.Connect):

            print "connection..."

            response = self.response_handler.decode_connection(self.con)

        else:

            print "response.."

            response = self.response_handler.decode(self.con)

            

        print "OK"

        

        return response

    

    def _collect_parts(self, header_list):

    

        body = []

        new_headers = []

        for header in header_list:

        

            if isinstance(header, headers.Body):

                body.append(header.data)

            elif isinstance(header, headers.End_Of_Body):

                body.append(header.data)

            else:

                new_headers.append(header)

        

        return new_headers, "".join(body)

    

    def connect(self, header_list = ()):

    

        """connect(self, header_list = ())

        

        Sends a connection message to the server and returns its response.

        Typically, the response is either Success or a subclass of

        FailureResponse.

        

        Specific headers can be sent by passing a sequence as the

        header_list keyword argument.

        """

        

        flags = 0

        data = (self.obex_version.to_byte(), flags, self.max_packet_length)

        

        max_length = self.max_packet_length

        request = requests.Connect(data)

        

        header_list = list(header_list)

        response = self._send_headers(request, header_list, max_length)

        

        if isinstance(response, responses.ConnectSuccess):

            self.remote_info = response

            for header in response.header_data:

                if isinstance(header, headers.Connection_ID):

                    # Recycle the Connection ID data to create a new header

                    # for future use.

                    self.connection_id = headers.Connection_ID(header.decode())



        return response

    

    def disconnect(self, header_list = ()):

    

        """disconnect(self, header_list = ())

        

        Sends a disconnection message to the server and returns its response.

        Typically, the response is either Success or a subclass of

        FailureResponse.

        

        Specific headers can be sent by passing a sequence as the

        header_list keyword argument.

        

        If the socket was not supplied using set_socket(), it will be closed.

        """

        

        max_length = self.remote_info.max_packet_length

        request = requests.Disconnect()

        

        header_list = list(header_list)

        response = self._send_headers(request, header_list, max_length)

                

        self.connection_id = None

        

        return response

        

    def mobex_cmd(self, typ, name=None, extra_headers=()):

        header_list = [

            headers.Type(typ),

        ]

        if name is not None:

            header_list.append(headers.Name(name))

        header_list += extra_headers

        

        max_length = self.remote_info.max_packet_length

        request = requests.Put_Final()

        

        return self._send_headers(request, header_list, max_length)

        

    # TODO: Make this prettier

    def ugly_basic_response_error_check(self, cmdName, resp):

        if not isinstance(resp, responses.Success):

            raise Exception("%s: Got an unexpected mobex response type: '%s'" % (cmdName, type(resp)))

        for hdr in resp.header_data:

            dataLwr = hdr.data.lower()

            if "fail" in dataLwr or "err" in dataLwr:

                raise Exception("%s: Received failure response: %s" % (cmdName, str(resp)))

        

    def mobex_connection_packet(self):

        return self.mobex_cmd("m-obex/connection_packet")

        

    def mobex_create_folder(self, dirPath):

        resp = self.mobex_cmd("m-obex/fs/folder_create", dirPath)

        self.ugly_basic_response_error_check("folder_create", resp)

        return resp

        

        

    def mobex_delete_file(self, filePath):

        resp = self.mobex_cmd("m-obex/fs/file_delete", filePath)

        self.ugly_basic_response_error_check("file_delete", resp)

        return resp

    

    def put(self, name, file_data, header_list = ()):

    

        """put(self, name, file_data, header_list = ())

        

        Sends a file with the given name, containing the file_data specified,

        to the server for storage in the current directory for the session,

        and returns the response.

        

        Additional headers can be sent by passing a sequence as the

        header_list keyword argument. These will be sent after the name and

        file length information associated with the name and file_data

        supplied.

        """

        

        header_list = [

            headers.Name(name),

            headers.Length(len(file_data))

            ] + list(header_list)

        

        max_length = self.remote_info.max_packet_length

        request = requests.Put()

        

        response = self._send_headers(request, header_list, max_length)

        

        if not isinstance(response, responses.Continue):

            return response

        

        # Send the file data.

        

        # The optimum size is the maximum packet length accepted by the

        # remote device minus three bytes for the header ID and length

        # minus three bytes for the request.

        optimum_size = max_length - 3 - 3

        

        i = 0

        while i < len(file_data):

        

            data = file_data[i:i+optimum_size]

            i += len(data)

            if i < len(file_data):

                request = requests.Put()

                request.add_header(headers.Body(data, False), max_length)

                self.con.send(request.encode())

                

                response = self.response_handler.decode(self.con)

                

                if not isinstance(response, responses.Continue):

                    return response

            

            else:

                request = requests.Put_Final()

                request.add_header(headers.End_Of_Body(data, False), max_length)

                self.con.send(request.encode())

                

                response = self.response_handler.decode(self.con)

                

                if not isinstance(response, responses.Success):

                    return response

        

        return response

    

    def get(self, name = None, header_list = ()):

    

        """get(self, name = None, header_list = ())

        

        Requests the specified file from the server's current directory for

        the session. If successful, returns a tuple containing a list of

        responses received during the operation and the file data received.

        If unsuccessful, a single response object is returned.

        

        Additional headers can be sent by passing a sequence as the

        header_list keyword argument. These will be sent after the name

        information.

        """

        

        header_list = list(header_list)

        if name is not None:

            header_list = [headers.Name(name)] + header_list

        

        max_length = self.remote_info.max_packet_length

        request = requests.Get()

        

        response = self._send_headers(request, header_list, max_length)

        

        if not isinstance(response, responses.Continue) and \

            not isinstance(response, responses.Success):

        

            return response

        

        # Retrieve the file data.

        returned_headers = []

        file_data = []

        request = requests.Get_Final()

        

        while isinstance(response, responses.Continue):

        

            returned_headers += response.header_data

            

            self.con.send(request.encode())

            

            response = self.response_handler.decode(self.con)

        

        if not isinstance(response, responses.Success):

            return response

        

        returned_headers += response.header_data

        

        return self._collect_parts(returned_headers)

    

    def setpath(self, name = "", create_dir = False, to_parent = False, header_list = ()):

    

        """setpath(self, name = "", create_dir = False, to_parent = False, header_list = ())

        

        Requests a change to the server's current directory for the session

        to the directory with the specified name, and returns the response.

        

        This method is also used to perform other actions, such as navigating

        to the parent directory (set to_parent to True) and creating a new

        directory (set create_dir to True).

        

        Additional headers can be sent by passing a sequence as the

        header_list keyword argument. These will be sent after the name

        information.

        """

        

        header_list = list(header_list)

        if name is not None:

            header_list = [headers.Name(name)] + header_list

        

        max_length = self.remote_info.max_packet_length

        

        flags = 0

        if not create_dir:

            flags |= requests.Set_Path.DontCreateDir

        if to_parent:

            flags |= requests.Set_Path.NavigateToParent

        

        request = requests.Set_Path((flags, 0))

        

        response = self._send_headers(request, header_list, max_length)

        return response

    

    def abort(self, header_list = ()):

    

        """abort(self, header_list = ())

        

        Aborts the current session and returns the server's response.

        

        Specific headers can be sent by passing a sequence as the

        header_list keyword argument.

        

        Warning: This method should only be called to terminate a running

        operation and is therefore only useful for developers who want to

        reimplementing existing operations.

        """

        

        header_list = list(header_list)

        max_length = self.remote_info.max_packet_length

        request = requests.Abort()

        

        response = self._send_headers(request, header_list, max_length)

        return response



class BrowserClient(Client):



    """BrowserClient(Client)

    

    client = BrowserClient(address, port)

    

    Provides an OBEX client that can be used to browse directories on a

    server via a folder-browsing service.

    

    The address used is a standard six-field bluetooth address, and the port

    should correspond to the port providing the folder-browsing service.

    

    To determine the correct port, examine the advertised services for a

    device by calling the bluetooth.find_service() function with the

    address of the device as the only argument.

    """

    

    def connect(self):

    

        targetName = "MOBEX\x00"

        return Client.connect(self, header_list = [headers.Target(targetName)])

    

    def capability(self):

    

        """capability(self)

        

        Returns a capability object from the server, or the server's response

        if the operation was unsuccessful.

        """

        

        response = self.get(header_list=[headers.Type("x-obex/capability")])

        if not isinstance(response, responses.Success):

            return response

        header, data = response

        return data

    

    def mobex_folder_list(self, folderPath):

    

        """listdir(self, name = "")

        

        Requests information about the contents of the directory with the

        specified name relative to the current directory for the session.

        Returns a tuple containing the server's response and the associated

        data.

        

        If successful, the directory contents are returned in the form of

        an XML document as described by the x-obex/folder-listing MIME type.

        

        If the name is omitted or an empty string is supplied, the contents

        of the current directory are typically listed by the server.

        """

        

        return self.mobex_cmd("m-obex/fs/folder-listing", folderPath)

        

    def mobex_file_list(self, folderPath):

        return self.mobex_cmd("m-obex/fs/file-listing", folderPath)

