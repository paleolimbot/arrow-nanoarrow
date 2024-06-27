# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# cython: language_level = 3

from nanoarrow_c cimport ArrowType

cdef class CArrowType:

    @staticmethod
    cdef ArrowType uninitialized()

    @staticmethod
    cdef bint is_unsigned_integer(ArrowType type_id)

    @staticmethod
    cdef bint is_signed_integer(ArrowType type_id)

    @staticmethod
    cdef bint is_floating_point(ArrowType type_id)

    @staticmethod
    cdef bint is_fixed_size(ArrowType type_id)

    @staticmethod
    cdef bint is_decimal(ArrowType type_id)

    @staticmethod
    cdef bint has_time_unit(ArrowType type_id)

    @staticmethod
    cdef bint is_union(ArrowType type_id)
