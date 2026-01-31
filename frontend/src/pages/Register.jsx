import React, { useState } from 'react';
import api from '../api';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
    const [step, setStep] = useState(1); // 1: Register, 2: OTP
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [debugOtp, setDebugOtp] = useState(''); // For demo purposes
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await api.post('/auth/register', { email, password });
            if (res.data.debug_otp) {
                setDebugOtp(res.data.debug_otp);
                alert(`Kayıt Başarılı. (DEBUG) OTP Kodunuz: ${res.data.debug_otp}`);
            } else {
                alert("Kayıt Başarılı. Lütfen emailinize gelen kodu giriniz.");
            }
            setStep(2);
        } catch (err) {
            alert(err.response?.data?.detail || "Bir hata oluştu");
        } finally {
            setLoading(false);
        }
    };

    const handleOtpVerify = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await api.post('/auth/verify-otp', { email, otp_code: otp });

            localStorage.setItem('access_token', res.data.access_token);
            localStorage.setItem('user', JSON.stringify(res.data.user));

            alert("Hesabınız doğrulandı! Yönlendiriliyorsunuz...");
            navigate('/dashboard');
        } catch (err) {
            alert(err.response?.data?.detail || "OTP Doğrulama başarısız");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-900 px-4 py-12 sm:px-6 lg:px-8">
            <div className="w-full max-w-md space-y-8 bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-white">
                        {step === 1 ? 'Ücretsiz Hesap Oluşturun' : 'Email Doğrulama'}
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-400">
                        {step === 1 ? 'Profesyonel WhatsApp Pazarlama Aracına Katılın' : `${email} adresine gönderilen 6 haneli kodu giriniz.`}
                    </p>
                    {step === 2 && debugOtp && (
                        <div className="mt-2 bg-yellow-900/50 p-2 rounded text-yellow-200 text-xs text-center border border-yellow-700">
                            Debug Mode: OTP is <b>{debugOtp}</b>
                        </div>
                    )}
                </div>

                {step === 1 ? (
                    <form className="mt-8 space-y-6" onSubmit={handleRegister}>
                        <div className="-space-y-px rounded-md shadow-sm">
                            <div>
                                <input
                                    type="email"
                                    required
                                    className="relative block w-full rounded-t-md border-0 bg-gray-700 py-3 px-3 text-white ring-1 ring-inset ring-gray-600 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-green-500 sm:text-sm sm:leading-6"
                                    placeholder="E-posta Adresi"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    type="password"
                                    required
                                    className="relative block w-full rounded-b-md border-0 bg-gray-700 py-3 px-3 text-white ring-1 ring-inset ring-gray-600 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-green-500 sm:text-sm sm:leading-6"
                                    placeholder="Şifre (Min 8 karakter)"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="group relative flex w-full justify-center rounded-md bg-green-600 px-3 py-3 text-sm font-semibold text-white hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600 disabled:opacity-50"
                            >
                                {loading ? 'İşleniyor...' : 'Kayıt Ol ve Kod Gönder'}
                            </button>
                        </div>
                    </form>
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleOtpVerify}>
                        <div>
                            <input
                                type="text"
                                required
                                maxLength="6"
                                className="block w-full text-center tracking-widest text-2xl rounded-md border-0 bg-gray-700 py-3 text-white ring-1 ring-inset ring-gray-600 placeholder:text-gray-500 focus:ring-2 focus:ring-green-500"
                                placeholder="000000"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                            />
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="group relative flex w-full justify-center rounded-md bg-green-600 px-3 py-3 text-sm font-semibold text-white hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600 disabled:opacity-50"
                            >
                                {loading ? 'Doğrulanıyor...' : 'Doğrula ve Giriş Yap'}
                            </button>
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="mt-4 w-full text-center text-sm text-gray-400 hover:text-white"
                            >
                                Geri Dön / Email Değiştir
                            </button>
                        </div>
                    </form>
                )}

                <div className="text-center mt-4">
                    <Link to="/login" className="text-sm text-green-400 hover:text-green-300">
                        Zaten hesabınız var mı? Giriş Yapın
                    </Link>
                </div>
            </div>
        </div>
    );
}
