
#include <stdio.h>
#include <gmp.h>
#include <time.h>
#include <Python.h>

static mpz_t n;
static mpz_t g;
static mpz_t n2;

static gmp_randstate_t state;

static void
_hec_init (const mpz_t pub_n, const mpz_t pub_g)
{
    mpz_init (n);
    mpz_init (g);
    mpz_init (n2);
    
    mpz_set (n, pub_n);
    mpz_set (g, pub_g);
    mpz_mul (n2, n, n);
    
    gmp_randinit_mt (state);
    unsigned long seed;
    FILE* fp = fopen ("/dev/urandom", "rb");
    if (fp == NULL)
        seed = time(NULL);
    else {
        fread (&seed, sizeof(unsigned long), 1, fp);
        fclose (fp);
    }
    gmp_randseed_ui (state, seed);
}

static void
_hec_quit (void)
{
    mpz_clear (n);
    mpz_clear (g);
    mpz_clear (n2);
    gmp_randclear (state);
}

static void
_hec_new (mpz_t v)
{
    mpz_t r;
    mpz_init (r);
    mpz_urandomm (r, state, n);
    mpz_powm (v, r, n, n2);
    mpz_clear (r);
}

static void
_hec_inc (mpz_t v_out, const mpz_t v_in, unsigned long inc)
{
    mpz_t r, v, w;
    mpz_init (r);
    mpz_init (v);
    mpz_init (w);
    mpz_urandomm (r, state, n);
    mpz_powm (v, r, n, n2);
    mpz_powm_ui (w, g, inc, n2);
    mpz_mul (v, v, w);
    mpz_mod (v, v, n2);
    mpz_mul (v, v, v_in);
    mpz_mod (v_out, v, n2);
    mpz_clear (r);
    mpz_clear (v);
    mpz_clear (w);
}

static unsigned long
_hec_get (const mpz_t v_in, const mpz_t pub_n,
          const mpz_t prv_l, const mpz_t prv_u)
{
    mpz_t v;
    mpz_init (v);
    mpz_mul (v, pub_n, pub_n);
	mpz_powm (v, v_in, prv_l, v);
	mpz_sub_ui (v, v, 1);
	mpz_tdiv_q (v, v, pub_n);
	mpz_mul (v, v, prv_u);
	mpz_mod (v, v, pub_n);
	unsigned long count = mpz_get_ui (v);
    mpz_clear (v);
    return count;
}

static PyObject *hecError;

static PyObject *
hec_init (PyObject *self, PyObject *args)
{
    const char* s_n;
    const char* s_g;
    if (!PyArg_ParseTuple(args, "ss", &s_n, &s_g))
        return NULL;

    mpz_t n, g;
    mpz_init (n);
    mpz_init (g);
    mpz_set_str (n, s_n, 10);
    mpz_set_str (g, s_g, 10);
    _hec_init (n, g);
    mpz_clear (n);
    mpz_clear (g);
        
    return Py_BuildValue ("i", 0);
}

static PyObject *
hec_new (PyObject *self, PyObject *args)
{
    mpz_t v;
    mpz_init (v);
    _hec_new (v);
    const char* s_val = mpz_get_str (NULL, 10, v);
    mpz_clear (v);

    return Py_BuildValue ("s", s_val);
}

static PyObject *
hec_inc (PyObject *self, PyObject *args)
{
    const char* s_in;
    unsigned long i_inc;
    if (!PyArg_ParseTuple(args, "sk", &s_in, &i_inc))
        return NULL;

    mpz_t v_in, v_out;
    mpz_init (v_in);
    mpz_init (v_out);
    mpz_set_str (v_in, s_in, 10);
    _hec_inc (v_out, v_in, i_inc);
    const char* s_val = mpz_get_str (NULL, 10, v_out);
    mpz_clear (v_in);
    mpz_clear (v_out);
        
    return Py_BuildValue ("s", s_val);
}

static PyObject *
hec_get (PyObject *self, PyObject *args)
{
    const char* s_n;
    const char* s_l;
    const char* s_u;
    const char* s_val;

    if (!PyArg_ParseTuple(args, "ssss", &s_val, &s_n, &s_l, &s_u))
        return NULL;

    mpz_t nn, l, u, v;
    mpz_init (nn);
    mpz_init (l);
    mpz_init (u);
    mpz_init (v);
    mpz_set_str (nn, s_n, 10);
    mpz_set_str (l, s_l, 10);
    mpz_set_str (u, s_u, 10);
    mpz_set_str (v, s_val, 10);
    unsigned long count = _hec_get (v, nn, l, u);
    mpz_clear (nn);
    mpz_clear (l);
    mpz_clear (u);
    mpz_clear (v);

    return Py_BuildValue ("k", count);
}

static PyObject *
hec_quit (PyObject *self, PyObject *args)
{
    _hec_quit();
    return Py_BuildValue ("i", 0);
}

static PyMethodDef hecMethods[] = {
    { "init",  hec_init, METH_VARARGS, "Initialize homomorphic encryption of counters."},
    { "new",   hec_new,  METH_VARARGS, "Create new counter."},
    { "inc",   hec_inc,  METH_VARARGS, "Increment counter."},
    { "get",   hec_get,  METH_VARARGS, "Get decrypted counter value."},
    { "quit",  hec_quit, METH_VARARGS, "Quit homomorphic encryption of counters."},
    { NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
inithec(void)
{
    PyObject *m = Py_InitModule ("hec", hecMethods);
    if (m == NULL)
        return;
    hecError = PyErr_NewException ("hec.error", NULL, NULL);
    Py_INCREF (hecError);
    PyModule_AddObject (m, "error", hecError);
}

