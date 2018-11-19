# -*- coding: utf-8 -*-

############################ Copyrights and license ###########################
#                                                                             #
# Copyright 2018 Rigas Papathanasopoulos <rigaspapas@gmail.com>               #
#                                                                             #
# This file is part of PyGithub.                                              #
# http://pygithub.readthedocs.io/                                             #
#                                                                             #
# PyGithub is free software: you can redistribute it and/or modify it under   #
# the terms of the GNU Lesser General Public License as published by the Free #
# Software Foundation, either version 3 of the License, or (at your option)   #
# any later version.                                                          #
#                                                                             #
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS   #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more#
# details.                                                                    #
#                                                                             #
# You should have received a copy of the GNU Lesser General Public License    #
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.            #
#                                                                             #
###############################################################################

import json
import urllib
from httplib import HTTPSConnection

import github.GithubObject
from github.AccessToken import AccessToken
from github.GithubException import GithubException
from github.MainClass import atLeastPython3


class ApplicationAuthorization(github.GithubObject.CompletableGithubObject):
    """
    This class is used for identifying and authorizing users for Github Apps.
    https://developer.github.com/apps/building-github-apps/identifying-and-authorizing-users-for-github-apps/#1-users-are-redirected-to-request-their-github-identity
    """

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None,
                 login=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.login = login

    @property
    def login_url(self):
        """
        Return the URL you need to redirect a user to in order to authorize
        your App.
        :type: string
        """
        params = {}
        possible_params = ['client_id', 'redirect_uri', 'state', 'login']
        for param in possible_params:
            value = getattr(self, param)
            if value is not None:
                params[param] = value

        if atLeastPython3:
            params = urllib.parse.urlencode(params)
        else:
            params = urllib.urlencode(params)

        base_url = 'https://github.com/login/oauth/authorize'
        return '{}?{}'.format(base_url, params)

    def get_access_token(self, code, state=None):
        """
        :calls: `POST /login/oauth/access_token <https://developer.github.com/apps/building-github-apps/identifying-and-authorizing-users-for-github-apps/>`_
        :param code: string
        """
        assert isinstance(code, (str, unicode)), code
        params = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if state is not None:
            params["state"] = state

        conn = HTTPSConnection("github.com")
        conn.request(
            method="POST",
            url="/login/oauth/access_token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "PyGithub/Python",
            },
            body=json.dumps(params),
        )
        response = conn.getresponse()
        response_text = response.read()

        if atLeastPython3:
            response_text = response_text.decode("utf-8")

        conn.close()
        if response.status >= 200 and response.status < 300:
            data = json.loads(response_text)
            return AccessToken(
                # not required, this is a NonCompletableGithubObject
                requester=None,
                # not required, this is a NonCompletableGithubObject
                headers={},
                attributes=data,
                completed=True
            )
        raise GithubException(
            status=response.status,
            data=response_text
        )
