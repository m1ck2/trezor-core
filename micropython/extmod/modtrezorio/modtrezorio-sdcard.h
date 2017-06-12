/*
 * Copyright (c) Pavol Rusnak, SatoshiLabs
 *
 * Licensed under TREZOR License
 * see LICENSE file for details
 */

#if defined TREZOR_STM32
#include "sdcard.h"
#elif defined TREZOR_UNIX
#include "unix-sdcard-mock.h"
#else
#error Unsupported TREZOR port. Only STM32 and UNIX ports are supported.
#endif

typedef struct _mp_obj_SDCard_t {
    mp_obj_base_t base;
} mp_obj_SDCard_t;

STATIC mp_obj_t mod_TrezorIO_SDCard_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 0, false);
    mp_obj_SDCard_t *o = m_new_obj(mp_obj_SDCard_t);
    o->base.type = type;
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t mod_TrezorIO_SDCard_present(mp_obj_t self) {
    return mp_obj_new_bool(sdcard_is_present());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_TrezorIO_SDCard_present_obj, mod_TrezorIO_SDCard_present);

STATIC mp_obj_t mod_TrezorIO_SDCard_power(mp_obj_t self, mp_obj_t state) {
    if (mp_obj_is_true(state)) {
        return mp_obj_new_bool(sdcard_power_on());
    } else {
        return mp_obj_new_bool(sdcard_power_off());
    }
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mod_TrezorIO_SDCard_power_obj, mod_TrezorIO_SDCard_power);

STATIC mp_obj_t mod_TrezorIO_SDCard_capacity(mp_obj_t self) {
    return mp_obj_new_int_from_ull(sdcard_get_capacity_in_bytes());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_TrezorIO_SDCard_capacity_obj, mod_TrezorIO_SDCard_capacity);

STATIC mp_obj_t mod_TrezorIO_SDCard_read(mp_obj_t self, mp_obj_t block_num, mp_obj_t buf) {
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf, &bufinfo, MP_BUFFER_WRITE);
    mp_uint_t ret = sdcard_read_blocks(bufinfo.buf, mp_obj_get_int(block_num), bufinfo.len / SDCARD_BLOCK_SIZE);
    return mp_obj_new_bool(ret == 0);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(mod_TrezorIO_SDCard_read_obj, mod_TrezorIO_SDCard_read);

STATIC mp_obj_t mod_TrezorIO_SDCard_write(mp_obj_t self, mp_obj_t block_num, mp_obj_t buf) {
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf, &bufinfo, MP_BUFFER_READ);
    mp_uint_t ret = sdcard_write_blocks(bufinfo.buf, mp_obj_get_int(block_num), bufinfo.len / SDCARD_BLOCK_SIZE);
    return mp_obj_new_bool(ret == 0);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(mod_TrezorIO_SDCard_write_obj, mod_TrezorIO_SDCard_write);

STATIC const mp_rom_map_elem_t mod_TrezorIO_SDCard_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_present), MP_ROM_PTR(&mod_TrezorIO_SDCard_present_obj) },
    { MP_ROM_QSTR(MP_QSTR_power), MP_ROM_PTR(&mod_TrezorIO_SDCard_power_obj) },
    { MP_ROM_QSTR(MP_QSTR_capacity), MP_ROM_PTR(&mod_TrezorIO_SDCard_capacity_obj) },
    { MP_ROM_QSTR(MP_QSTR_block_size), MP_OBJ_NEW_SMALL_INT(SDCARD_BLOCK_SIZE) },
    { MP_ROM_QSTR(MP_QSTR_read), MP_ROM_PTR(&mod_TrezorIO_SDCard_read_obj) },
    { MP_ROM_QSTR(MP_QSTR_write), MP_ROM_PTR(&mod_TrezorIO_SDCard_write_obj) },
};
STATIC MP_DEFINE_CONST_DICT(mod_TrezorIO_SDCard_locals_dict, mod_TrezorIO_SDCard_locals_dict_table);

STATIC const mp_obj_type_t mod_TrezorIO_SDCard_type = {
    { &mp_type_type },
    .name = MP_QSTR_SDCard,
    .make_new = mod_TrezorIO_SDCard_make_new,
    .locals_dict = (void*)&mod_TrezorIO_SDCard_locals_dict,
};