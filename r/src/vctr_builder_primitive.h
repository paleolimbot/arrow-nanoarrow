// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

#ifndef R_NANOARROW_VCTR_BUILDER_PRIMITIVE_H_INCLUDED
#define R_NANOARROW_VCTR_BUILDER_PRIMITIVE_H_INCLUDED

#define R_NO_REMAP
#include <R.h>
#include <Rinternals.h>

#include "vctr_builder_base.h"

class UnspecifiedBuilder : public VctrBuilder {
 public:
  explicit UnspecifiedBuilder(SEXP ptype_sexp)
      : VctrBuilder(VECTOR_TYPE_UNSPECIFIED, ptype_sexp) {}

  ArrowErrorCode Init(const ArrowSchema* schema, VctrBuilderOptions options,
                      ArrowError* error) override {
    NANOARROW_RETURN_NOT_OK(VctrBuilder::Init(schema, options, error));
    switch (schema_view_.type) {
      case NANOARROW_TYPE_DICTIONARY:
        StopCantConvert();
      default:
        break;
    }

    return NANOARROW_OK;
  }

  ArrowErrorCode Reserve(R_xlen_t n, ArrowError* error) override {
    NANOARROW_RETURN_NOT_OK(VctrBuilder::Reserve(n, error));
    value_ = PROTECT(Rf_allocVector(LGLSXP, n));
    SetValue(value_);
    UNPROTECT(1);
    return NANOARROW_OK;
  }

  ArrowErrorCode PushNext(const ArrowArray* array, ArrowError* error) override {
    int64_t not_null_count;
    if (array->null_count == -1 && array->buffers[0] == nullptr) {
      not_null_count = array->length;
    } else if (array->null_count == -1) {
      not_null_count =
          ArrowBitCountSet(reinterpret_cast<const uint8_t*>(array->buffers[0]),
                           array->offset, array->length);
    } else {
      not_null_count = array->length - array->null_count;
    }

    if (not_null_count > 0 && array->length > 0) {
      NANOARROW_RETURN_NOT_OK(
          WarnLossyConvert("that were non-null set to NA", not_null_count));
    }

    int* value_ptr = LOGICAL(value_) + value_size_;
    for (int64_t i = 0; i < array->length; i++) {
      value_ptr[i] = NA_LOGICAL;
    }

    return NANOARROW_OK;
  }
};

class IntBuilder : public VctrBuilder {
 public:
  explicit IntBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_INT, ptype_sexp) {}

  ArrowErrorCode Init(const ArrowSchema* schema, VctrBuilderOptions options,
                      ArrowError* error) override {
    NANOARROW_RETURN_NOT_OK(VctrBuilder::Init(schema, options, error));
    return NANOARROW_OK;
  }

  ArrowErrorCode Reserve(R_xlen_t n, ArrowError* error) override {
    NANOARROW_RETURN_NOT_OK(VctrBuilder::Reserve(n, error));
    value_ = PROTECT(Rf_allocVector(INTSXP, n));
    SetValue(value_);
    UNPROTECT(1);
    return NANOARROW_OK;
  }

  ArrowErrorCode PushNext(const ArrowArray* array, ArrowError* error) override {
    int* result = INTEGER(value_);
    int64_t n_bad_values = 0;

    // True for all the types supported here
    const uint8_t* is_valid = array_view_.buffer_views[0].data.as_uint8;
    int64_t raw_src_offset = array_view_.array->offset;
    R_xlen_t length = array->length;

    // Fill the buffer
    switch (array_view_.storage_type) {
      case NANOARROW_TYPE_NA:
        for (R_xlen_t i = 0; i < length; i++) {
          result[value_size_ + i] = NA_INTEGER;
        }
        break;
      case NANOARROW_TYPE_INT32:
        memcpy(result + value_size_,
               array_view_.buffer_views[1].data.as_int32 + raw_src_offset,
               length * sizeof(int32_t));

        // Set any nulls to NA_INTEGER
        if (is_valid != NULL && array_view_.array->null_count != 0) {
          for (R_xlen_t i = 0; i < length; i++) {
            if (!ArrowBitGet(is_valid, raw_src_offset + i)) {
              result[value_size_ + i] = NA_INTEGER;
            }
          }
        }
        break;
      case NANOARROW_TYPE_BOOL:
        ArrowBitsUnpackInt32(array_view_.buffer_views[1].data.as_uint8 + raw_src_offset,
                             raw_src_offset, length, result + value_size_);

        // Set any nulls to NA_LOGICAL
        if (is_valid != NULL && array_view_.array->null_count != 0) {
          for (R_xlen_t i = 0; i < length; i++) {
            if (!ArrowBitGet(is_valid, raw_src_offset + i)) {
              result[value_size_ + i] = NA_LOGICAL;
            }
          }
        }
        break;
      case NANOARROW_TYPE_INT8:
      case NANOARROW_TYPE_UINT8:
      case NANOARROW_TYPE_INT16:
      case NANOARROW_TYPE_UINT16:
        // No need to bounds check for these types
        for (R_xlen_t i = 0; i < length; i++) {
          result[value_size_ + i] = (int32_t)ArrowArrayViewGetIntUnsafe(&array_view_, i);
        }

        // Set any nulls to NA_INTEGER
        if (is_valid != NULL && array_view_.array->null_count != 0) {
          for (R_xlen_t i = 0; i < length; i++) {
            if (!ArrowBitGet(is_valid, raw_src_offset + i)) {
              result[value_size_ + i] = NA_INTEGER;
            }
          }
        }
        break;
      case NANOARROW_TYPE_UINT32:
      case NANOARROW_TYPE_INT64:
      case NANOARROW_TYPE_UINT64:
      case NANOARROW_TYPE_FLOAT:
      case NANOARROW_TYPE_DOUBLE:
        // Loop + bounds check. Because we don't know what memory might be
        // in a null slot, we have to check nulls if there are any.
        if (is_valid != NULL && array_view_.array->null_count != 0) {
          for (R_xlen_t i = 0; i < length; i++) {
            if (ArrowBitGet(is_valid, raw_src_offset + i)) {
              int64_t value = ArrowArrayViewGetIntUnsafe(&array_view_, i);
              if (value > INT_MAX || value <= NA_INTEGER) {
                result[value_size_ + i] = NA_INTEGER;
                n_bad_values++;
              } else {
                result[value_size_ + i] = (int32_t)value;
              }
            } else {
              result[value_size_ + i] = NA_INTEGER;
            }
          }
        } else {
          for (R_xlen_t i = 0; i < length; i++) {
            int64_t value = ArrowArrayViewGetIntUnsafe(&array_view_, i);
            if (value > INT_MAX || value <= NA_INTEGER) {
              result[value_size_ + i] = NA_INTEGER;
              n_bad_values++;
            } else {
              result[value_size_ + i] = (int32_t)value;
            }
          }
        }
        break;

      default:
        return EINVAL;
    }

    if (n_bad_values > 0) {
      warn_lossy_conversion(n_bad_values, "outside integer range set to NA");
    }

    return NANOARROW_OK;
  }

  SEXP GetPtype() override { return Rf_allocVector(INTSXP, 0); }
};

class DblBuilder : public VctrBuilder {
 public:
  explicit DblBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_DBL, ptype_sexp) {}

  SEXP GetPtype() override { return Rf_allocVector(REALSXP, 0); }
};

class LglBuilder : public VctrBuilder {
 public:
  explicit LglBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_LGL, ptype_sexp) {}

  SEXP GetPtype() override { return Rf_allocVector(LGLSXP, 0); }
};

class Integer64Builder : public VctrBuilder {
 public:
  explicit Integer64Builder(SEXP ptype_sexp)
      : VctrBuilder(VECTOR_TYPE_INTEGER64, ptype_sexp) {}
};

class ChrBuilder : public VctrBuilder {
 public:
  explicit ChrBuilder(SEXP ptype_sexp)
      : VctrBuilder(VECTOR_TYPE_CHR, ptype_sexp),
        use_altrep_(VCTR_BUILDER_USE_ALTREP_DEFAULT) {}

  SEXP GetPtype() override { return Rf_allocVector(STRSXP, 0); }

  VctrBuilderUseAltrep use_altrep_;
};

class BlobBuilder : public VctrBuilder {
 public:
  explicit BlobBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_BLOB, ptype_sexp) {}
};

class DateBuilder : public VctrBuilder {
 public:
  explicit DateBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_DATE, ptype_sexp) {}
};

class HmsBuilder : public VctrBuilder {
 public:
  explicit HmsBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_HMS, ptype_sexp) {}
};

class PosixctBuilder : public VctrBuilder {
 public:
  explicit PosixctBuilder(SEXP ptype_sexp)
      : VctrBuilder(VECTOR_TYPE_POSIXCT, ptype_sexp) {}
};

class DifftimeBuilder : public VctrBuilder {
 public:
  explicit DifftimeBuilder(SEXP ptype_sexp)
      : VctrBuilder(VECTOR_TYPE_DIFFTIME, ptype_sexp) {}
};

class OtherBuilder : public VctrBuilder {
 public:
  explicit OtherBuilder(SEXP ptype_sexp) : VctrBuilder(VECTOR_TYPE_OTHER, ptype_sexp) {}
};

#endif
