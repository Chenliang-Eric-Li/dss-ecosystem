#!/usr/bin/python
"""
 *   BSD LICENSE
 *
 *   Copyright (c) 2021 Samsung Electronics Co., Ltd.
 *   All rights reserved.
 *
 *   Redistribution and use in source and binary forms, with or without
 *   modification, are permitted provided that the following conditions
 *   are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in
 *       the documentation and/or other materials provided with the
 *       distribution.
 *     * Neither the name of Samsung Electronics Co., Ltd. nor the names of
 *       its contributors may be used to endorse or promote products derived
 *       from this software without specific prior written permission.
 *
 *   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 *   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 *   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os,sys
import dss
from datetime import datetime




class DssClientLib:
    def __init__(self, s3_endpoint, access_key, secret_key, logger=None):
        self.s3_endpoint = "http://" + s3_endpoint
        self.logger = logger
        self.dss_client = self.create_client(self.s3_endpoint, access_key, secret_key)

    def create_client(self, endpoint, access_key, secret_key):
        """
        Create dss_client
        :param endpoint:
        :param access_key:
        :param secret_key:
        :return:
        """
        dss_client = None
        try:
            dss_client =  dss.createClient(endpoint, access_key,secret_key)
            if not dss_client:
                self.logger.error("Failed to create s3 client from - {}".format(endpoint))
        except dss.DiscoverError as e:
            self.logger.exception("DiscoverError -  {}".format(e))
        except dss.NetworkError as e:
            #print("EXCEPTION: NetworkError - {}".format(e))
            self.logger.exception("NetworkError - {} , {}".format(endpoint, e))

        return dss_client

    def putObject(self, bucket=None,file=""):

        if file :
            object_key = file
            if file.startswith("/"):
                object_key = file[1:]
            try:
                ret = self.dss_client.putObject(object_key, file)
                if ret == 0:
                    return True
                elif ret == -1:
                    self.logger.error("Upload Failed for  key - {}".format(object_key))
            except dss.NoSuchResouceError as e:
                self.logger.exception("NoSuchResourceError putObject - {}".format(e))
            except dss.GenericError as e:
                self.logger.exception("putObject {}".format(e))
        return False

    def listObjects_old(self, bucket=None,  prefix="", delimiter="/"):
        object_keys = []
        try:
            object_keys = self.dss_client.listObjects(prefix, delimiter)
            #if object_keys:
            #    yield object_keys
        except dss.NoSuchResouceError as e:
            self.logger.exception("NoSuchResourceError - {}".format(e))
        except dss.GenericError as e:
            self.logger.exception("listObjects - {}".format(e))

        return object_keys

    def deleteObject(self, bucket=None, object_key=""):
        #self.logger.delete("......{}".format(object_key))
        if object_key:
            try:
                if self.dss_client.deleteObject(object_key) == 0:
                    return True
                elif self.dss_client.deleteObject(object_key) == -1:
                    self.logger.error("deleteObject filed for key - {}".format(object_key))
            except dss.NoSuchResouceError as e:
                self.logger.exception("deleteObject - {}, {}".format(object_key,e))
            except dss.GenericError as e:
                self.logger.exception("deleteObject - {}".format(e))
        return False


    def getObject(self, bucket=None, object_key="", dest_file_path=""):
        """
        Download the objects from S3 storage and store in a local or share path.
        :param bucket: None # Not required
        :param object_key: required to get object
        :param dest_file_path: file path in which object should be copied.
        :return:
        """
        if object_key and dest_file_path:
            try:
                return  self.dss_client.getObject(object_key, dest_file_path)
            except dss.NoSuchResouceError as e:
                self.logger.exception("NoSuchResourceError - getObject - {} , {}".format(object_key, e))
            except dss.GenericError as e:
                self.logger.exception("GenericError - getObject - {}".format(e))
        return False

    def listObjects(self, bucket=None,  prefix="", delimiter="/"):
        """
        List object keys under a specified prefix .
        :param bucket: None ( for dss_client ) , For minio and boto3 there should be an bucket already created.
        :param prefix: A object key prefix
        :param delimiter: Default is "/" to receive first level object keys.
        :return: List of object keys.
        """
        #obj_keys_count = 1000
        object_keys = []

        try:
            for obj_key in self.dss_client.getObjects(prefix, delimiter):
                object_keys.append(obj_key)
        except dss.NoSuchResouceError as e:
            self.logger.exception("NoSuchResourceError - {}".format(e))
        except dss.GenericError as e:
            self.logger.exception("listObjects - {}".format(e))

        return object_keys



if __name__ == "__main__":
    paths = ["/cat"]

    config="/home/somnath.s/work/nkv-datamover/conf.json"
    start_time = datetime.now()
    dss_client = DssClientLib("204.0.0.137:9000", "minio", "minio123")
    #dss_client = dss.createClient("http://202.0.0.103:9000", "minio", "minio123")
    print("INFO: DSS Client Connection Time: {}".format((datetime.now() - start_time).seconds))

    if dss_client:

        """
        for path in paths:
          for f in os.listdir(path):
            file_path = os.path.abspath(path + "/" + f)
            if not  dss_client.putObject(None, file_path):
                print("Failed to upload file - {}".format(file_path))
        """
        object_keys = dss_client.listObjects(None, "cat/")
        print("ListObjects: {}".format(object_keys))

        # getObject()
        for key in object_keys:
            if not dss_client.getObject(None, key, "/home/somnath.s/work/Testing/GET/"):
                print("ERROR: Failed to copy file for key - {}".format(key))





        print("Delete Objects!!!")
        for key in object_keys:
            print("INFO: Key-{}".format(key))
            if not dss_client.deleteObject(None, key):
                print("INFO: Failed to delete Object for key - {}".format(key))



        # Delete

